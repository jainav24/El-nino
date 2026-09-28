import pandas as pd
import numpy as np
import uuid
import joblib
import os
from sqlalchemy.orm import Session
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

from backend.database.models import Farmer, InsurancePolicy, InsuranceClaim, WeatherRecord, EnsoRecord, SurvivalDataset

# We will save models here
MODEL_DIR = "backend/ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

def build_survival_dataset(db: Session):
    """
    Builds the SurvivalDataset by joining the tables and performing feature engineering.
    """
    # 1. Load Data from Tables
    policies = pd.read_sql(db.query(InsurancePolicy).statement, db.bind)
    farmers = pd.read_sql(db.query(Farmer).statement, db.bind)
    claims = pd.read_sql(db.query(InsuranceClaim).statement, db.bind)
    weather = pd.read_sql(db.query(WeatherRecord).statement, db.bind)
    enso = pd.read_sql(db.query(EnsoRecord).statement, db.bind)
    
    if policies.empty or farmers.empty or weather.empty or enso.empty:
        raise ValueError("Insufficient data in database to build survival dataset.")

    # 2. Compute normal weather averages per region
    normal_weather = weather.groupby('region').agg({
        'rainfall': 'mean',
        'temperature': 'mean'
    }).rename(columns={'rainfall': 'normal_rainfall', 'temperature': 'normal_temperature'})
    
    # 3. Create survival dataset rows
    survival_records = []
    
    for _, policy in policies.iterrows():
        # Get Farmer
        farmer = farmers[farmers['farmer_id'] == policy['farmer_id']].iloc[0] if not farmers[farmers['farmer_id'] == policy['farmer_id']].empty else None
        if farmer is None:
            continue
            
        region = policy['region']
        
        # Get Policy Timeline
        start_date = pd.to_datetime(policy['policy_start_date'])
        end_date = pd.to_datetime(policy['policy_end_date'])
        
        # Get Claim (if any)
        policy_claims = claims[claims['policy_id'] == policy['policy_id']]
        if not policy_claims.empty:
            claim = policy_claims.iloc[0]
            claim_date = pd.to_datetime(claim['claim_date'])
            event = 1
            duration = (claim_date - start_date).days
        else:
            event = 0
            duration = (end_date - start_date).days
            
        # Ensure duration is positive
        if duration <= 0:
            duration = 1
            
        # Feature Engineering: Weather (Rolling values before policy start to prevent leakage)
        # We take weather in the region 3 months prior to policy start
        weather_region = weather[weather['region'] == region].copy()
        weather_region['date'] = pd.to_datetime(weather_region['date'])
        
        # Filter weather up to start date
        prior_weather = weather_region[weather_region['date'] <= start_date]
        if prior_weather.empty:
            prior_weather = weather_region # fallback
            
        recent_weather = prior_weather.tail(3)
        avg_rain = recent_weather['rainfall'].mean() if not recent_weather.empty else 0
        avg_temp = recent_weather['temperature'].mean() if not recent_weather.empty else 0
        avg_humidity = recent_weather['humidity'].mean() if not recent_weather.empty else 0
        avg_soil = recent_weather['soil_moisture'].mean() if not recent_weather.empty else 0
        
        norm_rain = normal_weather.loc[region, 'normal_rainfall'] if region in normal_weather.index else avg_rain
        norm_temp = normal_weather.loc[region, 'normal_temperature'] if region in normal_weather.index else avg_temp
        
        rain_anomaly = avg_rain - norm_rain
        temp_anomaly = avg_temp - norm_temp
        
        drought_indicator = 1 if (rain_anomaly < -20 and avg_soil < 0.3) else 0
        
        # Feature Engineering: ENSO (Value at policy start)
        enso_copy = enso.copy()
        enso_copy['date'] = pd.to_datetime(enso_copy['date'])
        prior_enso = enso_copy[enso_copy['date'] <= start_date]
        if prior_enso.empty:
            prior_enso = enso_copy
            
        current_enso = prior_enso.iloc[-1]
        oni_value = current_enso['oni_value']
        enso_phase = current_enso['enso_phase']
        enso_intensity = current_enso.get('enso_intensity', 'Neutral')
        enso_duration = current_enso.get('enso_duration', 0)
        
        el_nino_ind = 1 if enso_phase == 'El Niño' else 0
        la_nina_ind = 1 if enso_phase == 'La Niña' else 0
        
        # Interactions
        enso_x_rain = el_nino_ind * rain_anomaly
        enso_x_temp = el_nino_ind * temp_anomaly
        
        # Crop & Region encodings for interactions
        crop = farmer['crop_type']
        irrigation = farmer['irrigation_type']
        
        # We will keep raw categorical values for now, but compute a simple interaction term based on drought and crop vulnerability
        # E.g. Rice is highly vulnerable to drought
        drought_x_crop = 1 if drought_indicator == 1 and crop in ['Rice', 'Sugarcane'] else 0
        enso_x_crop = 1 if el_nino_ind == 1 and crop in ['Rice', 'Sugarcane'] else 0
        enso_x_region = 1 if el_nino_ind == 1 and region in ['Maharashtra', 'Karnataka'] else 0
        
        # Build record
        record = SurvivalDataset(
            policy_id=policy['policy_id'],
            farmer_id=policy['farmer_id'],
            duration=duration,
            event=event,
            rainfall=avg_rain,
            temperature=avg_temp,
            humidity=avg_humidity,
            soil_moisture=avg_soil,
            rainfall_anomaly=rain_anomaly,
            temperature_anomaly=temp_anomaly,
            rolling_rainfall=avg_rain,
            rolling_temperature=avg_temp,
            drought_indicator=drought_indicator,
            oni_value=oni_value,
            enso_phase=enso_phase,
            enso_intensity=enso_intensity,
            enso_duration=enso_duration,
            el_nino_indicator=el_nino_ind,
            la_nina_indicator=la_nina_ind,
            crop_type=crop,
            region=region,
            farm_area=farmer['farm_area'],
            soil_type=farmer['soil_type'],
            irrigation_type=irrigation,
            enso_x_rainfall_anomaly=enso_x_rain,
            enso_x_temp_anomaly=enso_x_temp,
            drought_x_crop=drought_x_crop,
            enso_x_crop=enso_x_crop,
            enso_x_region=enso_x_region
        )
        survival_records.append(record)
        
    # Delete old dataset and insert new
    db.query(SurvivalDataset).delete()
    db.add_all(survival_records)
    db.commit()
    
    return len(survival_records)


def train_cox_model(db: Session):
    """
    Trains the Cox Proportional Hazards model using the SurvivalDataset.
    """
    records = pd.read_sql(db.query(SurvivalDataset).statement, db.bind)
    if records.empty:
        raise ValueError("Survival dataset is empty. Cannot train.")
        
    df = records.copy()
    
    # Preprocessing
    # Drop IDs
    df = df.drop(columns=['id', 'policy_id', 'farmer_id'])
    
    # Encode categoricals
    cat_cols = ['enso_phase', 'enso_intensity', 'crop_type', 'region', 'soil_type', 'irrigation_type']
    
    # Save categories for prediction
    categories = {}
    for col in cat_cols:
        categories[col] = df[col].unique().tolist()
        df[col] = df[col].astype('category')
        
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True, dtype=float)
    
    # Ensure no weird object columns left (e.g. from SQLAlchemy)
    df = df.select_dtypes(exclude=['object'])
    
    # Fill NA and convert everything to float
    df = df.fillna(0).astype(float)
    
    # Drop columns with zero variance
    for col in df.columns:
        if df[col].var() == 0:
            df = df.drop(columns=[col])
            print(f"Dropped zero-variance column: {col}")
            
    # Train Cox Model
    cph = CoxPHFitter(penalizer=0.01)
    
    try:
        cph.fit(df, duration_col='duration', event_col='event')
    except Exception as e:
        # If perfect collinearity or issues, drop problematic columns
        from lifelines.exceptions import ConvergenceError
        print(f"Convergence issue: {e}")
        raise ValueError(f"Model failed to converge: {str(e)}")
        
    c_index = cph.concordance_index_
    
    # Save model and columns
    model_path = os.path.join(MODEL_DIR, "cox_ph_model.joblib")
    cols_path = os.path.join(MODEL_DIR, "expected_columns.joblib")
    cat_path = os.path.join(MODEL_DIR, "categories.joblib")
    
    joblib.dump(cph, model_path)
    joblib.dump(list(df.columns), cols_path)
    joblib.dump(categories, cat_path)
    
    return {
        "c_index": c_index,
        "dataset_size": len(df),
        "features": list(df.columns),
        "summary": cph.summary.reset_index().to_dict(orient='records')
    }
