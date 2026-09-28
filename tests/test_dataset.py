import pandas as pd
import pytest
import os

def test_raw_dataset_schema():
    path = "data/raw/raw_unclean_dataset.csv"
    assert os.path.exists(path), "Dataset not found"
    
    df = pd.read_csv(path)
    
    # Check shape
    assert len(df) == 10000
    assert len(df.columns) == 33
    
    # Verify leak variables are not used as targets implicitly
    assert 'claim_count' in df.columns
    assert 'claim_occurred' in df.columns
    assert 'time_to_claim' in df.columns
    
    # Test valid values
    assert df['elnino_status'].isin(['Active El Nino', 'La Nina', 'Neutral']).all()
    assert df['enso_index'].min() >= -3.0 and df['enso_index'].max() <= 3.0
    
    # Test censoring exists
    censor_rate = 1.0 - df['claim_occurred'].mean()
    assert 0.05 < censor_rate < 0.95, "Censoring rate is unrealistic"

def test_ml_dataset_schema():
    path = "data/processed/ml_pipeline_output/survival_analysis_dataset.csv"
    assert os.path.exists(path), "ML dataset not found"
    
    df = pd.read_csv(path)
    
    # Ensure leaked columns were dropped during feature engineering
    assert 'claim_count' not in df.columns
    assert 'current_yield' not in df.columns
    assert 'policy_id' not in df.columns
