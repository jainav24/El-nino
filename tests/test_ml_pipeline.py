import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from ml.preprocessing import clean_dates, handle_missing_values, remove_duplicates
from ml.feature_engineering import create_weather_features, create_enso_features
from ml.survival_dataset import build_survival_dataset
from ml.validation import validate_no_leakage

@pytest.fixture
def sample_weather():
    return pd.DataFrame({
        "region": ["TestRegion", "TestRegion", "TestRegion"],
        "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "rainfall": [10, 20, np.nan],
        "temperature": [25, 26, 27],
        "humidity": [60, 65, 70],
        "soil_moisture": [30, 32, 34]
    })

@pytest.fixture
def sample_enso():
    return pd.DataFrame({
        "date": ["2023-01-01", "2023-02-01"],
        "oni_value": [1.5, 1.6],
        "enso_phase": ["El Niño", "El Niño"]
    })

@pytest.fixture
def sample_policies():
    return pd.DataFrame({
        "policy_id": ["P1", "P2"],
        "farmer_id": ["F1", "F2"],
        "crop_type": ["Wheat", "Rice"],
        "region": ["TestRegion", "TestRegion"],
        "policy_start_date": ["2023-01-01", "2023-01-01"],
        "policy_end_date": ["2023-01-31", "2023-01-31"],
        "insured_amount": [10000, 20000]
    })

@pytest.fixture
def sample_claims():
    return pd.DataFrame({
        "claim_id": ["C1"],
        "policy_id": ["P1"],
        "claim_date": ["2023-01-15"],
        "claim_amount": [5000],
        "claim_status": ["Approved"]
    })

def test_missing_values(sample_weather):
    df = handle_missing_values(sample_weather, {"rainfall": "mean"})
    assert df['rainfall'].isna().sum() == 0
    assert df['rainfall'].iloc[2] == 15.0 # (10+20)/2

def test_clean_dates(sample_weather):
    df = clean_dates(sample_weather, ["date"])
    assert pd.api.types.is_datetime64_any_dtype(df['date'])

def test_weather_features(sample_weather):
    df = handle_missing_values(sample_weather, {"rainfall": "mean"})
    df = clean_dates(df, ["date"])
    df_feat = create_weather_features(df, window_days=2)
    assert 'rainfall_anomaly' in df_feat.columns
    assert 'cumulative_rainfall_30d' in df_feat.columns

def test_enso_features(sample_enso):
    df = create_enso_features(sample_enso)
    assert df['el_nino_indicator'].iloc[0] == 1
    assert df['la_nina_indicator'].iloc[0] == 0

def test_survival_dataset(sample_policies, sample_claims, sample_weather, sample_enso):
    # Setup formats
    w = clean_dates(handle_missing_values(sample_weather, {"rainfall": "mean"}), ["date"])
    e = clean_dates(sample_enso, ["date"])
    p = clean_dates(sample_policies, ["policy_start_date", "policy_end_date"])
    c = clean_dates(sample_claims, ["claim_date"])
    
    # Run pipeline
    df_final = build_survival_dataset(p, c, w, e)
    
    assert len(df_final) == 2
    
    # P1 had a claim on 2023-01-15. Start was 2023-01-01. Duration = 14 days. Event = 1
    p1 = df_final[df_final['policy_id'] == 'P1'].iloc[0]
    assert p1['event'] == 1
    assert p1['duration'] == 14
    
    # P2 had no claim. Start 2023-01-01, end 2023-01-31. Duration = 30 days. Event = 0
    p2 = df_final[df_final['policy_id'] == 'P2'].iloc[0]
    assert p2['event'] == 0
    assert p2['duration'] == 30

def test_no_leakage(sample_policies, sample_claims, sample_weather, sample_enso):
    w = clean_dates(handle_missing_values(sample_weather, {"rainfall": "mean"}), ["date"])
    e = clean_dates(sample_enso, ["date"])
    p = clean_dates(sample_policies, ["policy_start_date", "policy_end_date"])
    c = clean_dates(sample_claims, ["claim_date"])
    
    df_final = build_survival_dataset(p, c, w, e)
    
    assert validate_no_leakage(df_final) == True
