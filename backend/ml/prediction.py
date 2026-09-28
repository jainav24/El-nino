import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = "backend/ml/models"

def get_active_model_info():
    model_path = os.path.join(MODEL_DIR, "cox_ph_model.joblib")
    if not os.path.exists(model_path):
        return None
    return True

def predict_risk(data: dict):
    model_path = os.path.join(MODEL_DIR, "cox_ph_model.joblib")
    cols_path = os.path.join(MODEL_DIR, "expected_columns.joblib")
    cat_path = os.path.join(MODEL_DIR, "categories.joblib")
    
    if not os.path.exists(model_path):
        raise ValueError("Model not trained yet.")
        
    cph = joblib.load(model_path)
    expected_cols = joblib.load(cols_path)
    categories = joblib.load(cat_path)
    
    # Preprocess inputs identical to training
    # For a real scenario, inputs come from frontend form.
    
    # Determine el_nino / la_nina indicators
    enso_phase = data.get('enso_phase', 'Neutral')
    el_nino_ind = 1 if enso_phase == 'El Niño' else 0
    la_nina_ind = 1 if enso_phase == 'La Niña' else 0
    
    rain_anomaly = data.get('rainfall_anomaly_pct', 0.0)
    temp_anomaly = data.get('temp_anomaly_c', 0.0)
    
    crop = data.get('crop_type', '')
    region = data.get('region', '')
    
    # Drought logic
    drought_ind = data.get('drought_index', 0.0)
    
    df = pd.DataFrame([{
        'rainfall': data.get('rainfall_mm', 0.0),
        'temperature': data.get('temperature_c', 0.0),
        'humidity': data.get('humidity_pct', 0.0),
        'soil_moisture': 0.0,
        'rainfall_anomaly': rain_anomaly,
        'temperature_anomaly': temp_anomaly,
        'rolling_rainfall': data.get('rainfall_mm', 0.0),
        'rolling_temperature': data.get('temperature_c', 0.0),
        'drought_indicator': drought_ind,
        'oni_value': data.get('oni', 0.0),
        'enso_phase': enso_phase,
        'enso_intensity': data.get('enso_intensity', 'Neutral'),
        'enso_duration': 0,
        'el_nino_indicator': el_nino_ind,
        'la_nina_indicator': la_nina_ind,
        'crop_type': crop,
        'region': region,
        'farm_area': data.get('farm_area_acres', 1.0),
        'soil_type': data.get('soil_type', ''),
        'irrigation_type': data.get('irrigation', ''),
        'enso_x_rainfall_anomaly': el_nino_ind * rain_anomaly,
        'enso_x_temp_anomaly': el_nino_ind * temp_anomaly,
        'drought_x_crop': 1 if drought_ind > 0 and crop in ['Rice', 'Sugarcane'] else 0,
        'enso_x_crop': 1 if el_nino_ind == 1 and crop in ['Rice', 'Sugarcane'] else 0,
        'enso_x_region': 1 if el_nino_ind == 1 and region in ['Maharashtra', 'Karnataka'] else 0
    }])
    
    for col, cats in categories.items():
        if col in df.columns:
            df[col] = pd.Categorical(df[col], categories=cats)
            
    df = pd.get_dummies(df, columns=list(categories.keys()), drop_first=True)
    
    # Align columns
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0
    
    # Keep only expected columns in exact order
    df = df[expected_cols]
    
    # Ignore time to event and event which shouldn't be in expected cols anyway
    if 'duration' in df.columns:
        df = df.drop(columns=['duration', 'event'])
        expected_cols = [c for c in expected_cols if c not in ('duration', 'event')]
        df = df[expected_cols]

    # Predict Hazard
    hazard_ratio = float(np.exp(cph.predict_partial_hazard(df).iloc[0]))
    
    # Extract Risk Factors
    # risk factor contribution = input_value * coefficient
    # For Cox PH, partial hazard = exp(sum(beta_i * x_i))
    contributions = {}
    if hasattr(cph, 'params_'):
        params = cph.params_
        for col in df.columns:
            val = df[col].iloc[0]
            coef = params.get(col, 0)
            if val != 0 and coef != 0:
                # We can report exp(coef) as the hazard ratio for that feature
                contributions[col] = float(np.exp(coef))
    else:
        # Fallback if params_ is not available
        contributions = {"Rainfall Anomaly": 1.2, "Temperature Anomaly": 1.1}
        
    # Sort contributions by magnitude of difference from 1.0
    sorted_factors = sorted(contributions.items(), key=lambda item: abs(item[1] - 1.0), reverse=True)
    top_factors = [{"factor": k.replace('_', ' ').title(), "hazard_ratio": v} for k, v in sorted_factors[:4]]
    
    # Predict Survival Function
    surv_func = cph.predict_survival_function(df)
    times = [30, 60, 90, 120]
    survival_probs = {}
    
    for t in times:
        # get closest time
        closest_t = min(surv_func.index, key=lambda x: abs(x - t))
        survival_probs[f"{t}_days"] = float(surv_func.loc[closest_t].iloc[0])
        
    from backend.config import RISK_THRESHOLDS
    
    # Categories
    if hazard_ratio > RISK_THRESHOLDS["HIGH"]:
        category = "HIGH"
    elif hazard_ratio > RISK_THRESHOLDS["MEDIUM"]:
        category = "MEDIUM"
    else:
        category = "LOW"
        
    return {
        "risk_category": category,
        "relative_hazard": hazard_ratio,
        "survival_probabilities": survival_probs,
        "risk_factors": top_factors
    }
