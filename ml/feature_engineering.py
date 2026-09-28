import pandas as pd
import numpy as np

def create_weather_features(df_weather: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
    """
    Generate rolling statistics and anomalies for weather data.
    Assumes df_weather is sorted by date and grouped by region if applied outside.
    We will sort it inside just in case.
    """
    df = df_weather.copy()
    if 'date' in df.columns:
        df = df.sort_values(by=['region', 'date'])
        
    # Calculate historical means per region for anomaly calculation
    historical_means = df.groupby('region')[['rainfall', 'temperature', 'humidity', 'soil_moisture']].transform('mean')
    
    df['rainfall_anomaly'] = df['rainfall'] - historical_means['rainfall']
    df['temperature_anomaly'] = df['temperature'] - historical_means['temperature']
    df['humidity_anomaly'] = df['humidity'] - historical_means['humidity']
    df['soil_moisture_anomaly'] = df['soil_moisture'] - historical_means['soil_moisture']
    
    # Drought indicator: High temp anomaly + low rainfall anomaly + low soil moisture
    df['drought_indicator'] = np.where(
        (df['temperature_anomaly'] > 0) & 
        (df['rainfall_anomaly'] < 0) & 
        (df['soil_moisture_anomaly'] < 0), 1, 0
    )
    
    # Rolling features using window_days (approximation using rows if strictly daily data, 
    # but best to use rolling on a datetime index if possible. Assuming daily data here).
    df['cumulative_rainfall_30d'] = df.groupby('region')['rainfall'].transform(lambda x: x.rolling(window_days, min_periods=1).sum())
    df['rolling_rainfall_mean'] = df.groupby('region')['rainfall'].transform(lambda x: x.rolling(window_days, min_periods=1).mean())
    df['rolling_temp_mean'] = df.groupby('region')['temperature'].transform(lambda x: x.rolling(window_days, min_periods=1).mean())
    
    return df

def create_enso_features(df_enso: pd.DataFrame) -> pd.DataFrame:
    """
    Create binary indicators and format ENSO features.
    """
    df = df_enso.copy()
    
    df['el_nino_indicator'] = (df['enso_phase'].str.lower() == 'el niño').astype(int)
    df['la_nina_indicator'] = (df['enso_phase'].str.lower() == 'la niña').astype(int)
    df['neutral_indicator'] = (df['enso_phase'].str.lower() == 'neutral').astype(int)
    
    return df

def create_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create interaction features between ENSO, weather, and agricultural factors.
    Requires a merged DataFrame containing both weather anomalies and ENSO indicators.
    """
    df_feat = df.copy()
    
    # ENSO x Weather
    if 'el_nino_indicator' in df_feat.columns and 'rainfall_anomaly' in df_feat.columns:
        df_feat['enso_x_rainfall_anomaly'] = df_feat['el_nino_indicator'] * df_feat['rainfall_anomaly']
        df_feat['enso_x_temp_anomaly'] = df_feat['el_nino_indicator'] * df_feat['temperature_anomaly']
        
    # ENSO x Crop / Region (Requires one-hot encoding first for numerical multiplication, 
    # but for tree-based models categorical strings might suffice. For CoxPH we need numeric).
    # We will assume dummy variables are created later or we create specific cross features here.
    # E.g., a simple vulnerability score could be assigned, but for raw interaction:
    # df_feat['enso_x_crop'] will be created during dummy encoding in the pipeline before model training.
    
    # Drought x Crop interaction is also easier handled via dummy encoding, but we can flag it.
    
    return df_feat
