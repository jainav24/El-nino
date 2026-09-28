"""
Configuration for the ML preprocessing and feature engineering pipeline.
"""

EXPECTED_COLUMNS = {
    "weather": ["region", "date", "rainfall", "temperature", "humidity", "soil_moisture"],
    "enso": ["date", "oni_value", "enso_phase"],
    "policies": ["policy_id", "farmer_id", "crop_type", "region", "policy_start_date", "policy_end_date", "insured_amount"],
    "claims": ["claim_id", "policy_id", "claim_date", "claim_amount", "claim_status"],
    "farmers": ["farmer_id", "region", "farm_area", "crop_type", "soil_type", "irrigation_type"]
}

CATEGORICAL_COLUMNS = ["crop_type", "region", "soil_type", "irrigation_type", "enso_phase"]

NUMERICAL_COLUMNS = ["rainfall", "temperature", "humidity", "soil_moisture", "oni_value", "farm_area", "insured_amount"]

# Anomalies are calculated using these rolling windows (in days for weather, or months for ENSO)
ROLLING_WINDOW_DAYS = 30
