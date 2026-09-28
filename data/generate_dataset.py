"""
Synthetic Agricultural Insurance Dataset Generator
====================================================
Generates a realistic synthetic dataset for survival analysis of
agricultural insurance claims under El Niño weather anomalies.

Schema matches the 33-column format expected by the ML pipeline:
  policy_id, farmer_id, state, district, latitude, longitude,
  crop_type, crop_season, farm_area, soil_type, irrigation_type,
  elnino_status, enso_index, elnino_intensity, normal_rainfall,
  rainfall, rainfall_deviation, temperature, temperature_deviation,
  humidity, soil_moisture, drought_index, flood_index,
  extreme_weather_events, weather_anomaly_score, historical_yield,
  current_yield, insurance_amount, premium_amount, previous_claims,
  claim_count, time_to_claim, claim_occurred

NOTE: `current_yield` and `claim_count` are generated for dataset
completeness but are EXCLUDED from model training to prevent data leakage.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
NUM_POLICIES = 10000

# ──────────────────────────────────────────────
# Domain Constants (must match backend/ml/risk_engine.py)
# ──────────────────────────────────────────────
STATES = ['Andhra Pradesh', 'Karnataka', 'Madhya Pradesh',
          'Maharashtra', 'Punjab', 'Uttar Pradesh']

DISTRICTS = {
    'Andhra Pradesh': ['Guntur', 'Krishna', 'Kurnool', 'Prakasam'],
    'Karnataka': ['Belgaum', 'Dharwad', 'Raichur', 'Shimoga'],
    'Madhya Pradesh': ['Indore', 'Jabalpur', 'Sagar', 'Ujjain'],
    'Maharashtra': ['Nashik', 'Pune', 'Solapur', 'Wardha'],
    'Punjab': ['Amritsar', 'Jalandhar', 'Ludhiana', 'Patiala'],
    'Uttar Pradesh': ['Agra', 'Allahabad', 'Lucknow', 'Varanasi'],
}

LAT_LON = {
    'Andhra Pradesh': (15.5, 79.5),
    'Karnataka': (15.0, 75.7),
    'Madhya Pradesh': (23.5, 78.0),
    'Maharashtra': (19.0, 75.0),
    'Punjab': (31.0, 75.5),
    'Uttar Pradesh': (27.0, 81.0),
}

CROP_TYPES = ['Cotton', 'Maize', 'Rice', 'Soybean', 'Sugarcane', 'Wheat']
CROP_SEASONS = ['Kharif', 'Rabi', 'Zaid']
SOIL_TYPES = ['Alluvial', 'Black', 'Laterite', 'Loamy', 'Red']
IRRIGATION_TYPES = ['Canal', 'Drip', 'Rainfed', 'Tube Well']

ELNINO_STATUSES = ['Active El Nino', 'La Nina', 'Neutral']
ELNINO_INTENSITIES = ['La Nina', 'Moderate El Nino', 'Strong El Nino', 'Weak El Nino']

# ──────────────────────────────────────────────
# 1. Generate Base Features
# ──────────────────────────────────────────────
states = np.random.choice(STATES, NUM_POLICIES)
districts = [np.random.choice(DISTRICTS[s]) for s in states]

latitudes = np.array([LAT_LON[s][0] + np.random.uniform(-1.5, 1.5) for s in states])
longitudes = np.array([LAT_LON[s][1] + np.random.uniform(-1.5, 1.5) for s in states])

crop_types = np.random.choice(CROP_TYPES, NUM_POLICIES, p=[0.15, 0.15, 0.25, 0.15, 0.15, 0.15])
crop_seasons = np.random.choice(CROP_SEASONS, NUM_POLICIES, p=[0.45, 0.40, 0.15])
soil_types = np.random.choice(SOIL_TYPES, NUM_POLICIES)
irrigation_types = np.random.choice(IRRIGATION_TYPES, NUM_POLICIES, p=[0.20, 0.15, 0.45, 0.20])
farm_areas = np.round(np.random.lognormal(mean=1.5, sigma=0.8, size=NUM_POLICIES).clip(0.1, 500), 2)

# ──────────────────────────────────────────────
# 2. ENSO / El Niño Features
# ──────────────────────────────────────────────
elnino_statuses = np.random.choice(ELNINO_STATUSES, NUM_POLICIES, p=[0.30, 0.20, 0.50])

# ENSO index correlated with status
enso_indices = np.where(
    elnino_statuses == 'Active El Nino',
    np.random.uniform(0.5, 2.8, NUM_POLICIES),
    np.where(
        elnino_statuses == 'La Nina',
        np.random.uniform(-2.5, -0.5, NUM_POLICIES),
        np.random.uniform(-0.49, 0.49, NUM_POLICIES)
    )
)
enso_indices = np.round(enso_indices, 2)

# Intensity derived from ENSO index
elnino_intensities = np.where(
    enso_indices >= 1.5, 'Strong El Nino',
    np.where(enso_indices >= 1.0, 'Moderate El Nino',
    np.where(enso_indices >= 0.5, 'Weak El Nino',
    'La Nina'))
)
# Override for negative indices
elnino_intensities = np.where(enso_indices <= -0.5, 'La Nina', elnino_intensities)

# ──────────────────────────────────────────────
# 3. Weather Features (correlated with El Niño)
# ──────────────────────────────────────────────
# Normal rainfall by state (mm per season)
state_normal_rainfall = {
    'Andhra Pradesh': 700, 'Karnataka': 650, 'Madhya Pradesh': 900,
    'Maharashtra': 750, 'Punjab': 500, 'Uttar Pradesh': 800,
}
normal_rainfalls = np.array([state_normal_rainfall[s] + np.random.normal(0, 100) for s in states])
normal_rainfalls = np.clip(np.round(normal_rainfalls, 1), 100, 3000)

# El Niño reduces rainfall in India (monsoon disruption)
rainfall_factor = np.where(
    elnino_statuses == 'Active El Nino',
    np.random.uniform(0.4, 0.85, NUM_POLICIES),   # 15-60% reduction
    np.where(
        elnino_statuses == 'La Nina',
        np.random.uniform(1.0, 1.5, NUM_POLICIES),  # 0-50% increase
        np.random.uniform(0.8, 1.2, NUM_POLICIES)    # near normal
    )
)
rainfalls = np.round(normal_rainfalls * rainfall_factor, 1)
rainfalls = np.clip(rainfalls, 0, 5000)
rainfall_deviations = np.round(rainfalls - normal_rainfalls, 1)

# Temperature (El Niño → hotter)
base_temp = np.where(
    elnino_statuses == 'Active El Nino',
    np.random.normal(33, 2.5, NUM_POLICIES),
    np.where(
        elnino_statuses == 'La Nina',
        np.random.normal(26, 2, NUM_POLICIES),
        np.random.normal(28, 2, NUM_POLICIES)
    )
)
temperatures = np.round(np.clip(base_temp, 5, 50), 1)
temperature_deviations = np.round(temperatures - 28.0, 1)

# Humidity (inversely related to El Niño in South Asia)
humidities = np.where(
    elnino_statuses == 'Active El Nino',
    np.random.normal(45, 12, NUM_POLICIES),
    np.where(
        elnino_statuses == 'La Nina',
        np.random.normal(75, 10, NUM_POLICIES),
        np.random.normal(65, 10, NUM_POLICIES)
    )
)
humidities = np.round(np.clip(humidities, 10, 100), 1)

# Soil moisture
soil_moistures = np.round(np.clip(
    rainfalls / (normal_rainfalls * 2) + np.random.normal(0, 0.08, NUM_POLICIES),
    0.01, 1.0
), 2)

# Drought & Flood indices
drought_indices = np.round(np.clip(1.0 - soil_moistures + (temperature_deviations > 2).astype(float) * 0.15, 0, 1), 2)
flood_indices = np.round(np.clip((rainfall_deviations / 800.0), 0, 1), 2)

# Extreme weather events count
extreme_weather_events = np.where(
    elnino_statuses == 'Active El Nino',
    np.random.poisson(4, NUM_POLICIES),
    np.where(
        elnino_statuses == 'La Nina',
        np.random.poisson(3, NUM_POLICIES),
        np.random.poisson(1.5, NUM_POLICIES)
    )
).clip(0, 30)

# Weather anomaly score (composite 0–1)
weather_anomaly_scores = np.round(np.clip(
    drought_indices * 0.4 + flood_indices * 0.3 + (extreme_weather_events / 20) * 0.3,
    0, 1
), 2)

# ──────────────────────────────────────────────
# 4. Agricultural & Insurance Features
# ──────────────────────────────────────────────
historical_yields = np.round(np.random.uniform(500, 8000, NUM_POLICIES), 1)
current_yields = np.round(historical_yields * rainfall_factor * np.random.uniform(0.7, 1.1, NUM_POLICIES), 1)

insurance_amounts = np.round(farm_areas * np.random.uniform(8000, 50000, NUM_POLICIES), 0)
premium_amounts = np.round(insurance_amounts * np.random.uniform(0.02, 0.08, NUM_POLICIES), 0)

previous_claims = np.random.poisson(lam=0.8, size=NUM_POLICIES).clip(0, 20)

# ──────────────────────────────────────────────
# 5. Survival Targets: time_to_claim & claim_occurred
# ──────────────────────────────────────────────
# Hazard model: factors that increase claim probability
# El Niño effect is made STRONGER for academic demonstration
hazard_score = (
    enso_indices * 0.8                                          # Strong El Niño effect
    + (irrigation_types == 'Rainfed').astype(int) * 1.5         # Rainfed vulnerability
    - (irrigation_types == 'Drip').astype(int) * 0.6            # Drip irrigation is protective
    + drought_indices * 2.0                                     # Drought impact
    + flood_indices * 1.2                                       # Flood impact
    + (temperature_deviations / 5.0)                            # Temperature stress
    - soil_moistures * 1.5                                      # Adequate moisture is protective
    + previous_claims * 0.4                                     # Moral hazard / adverse selection
    + extreme_weather_events * 0.15                             # Extreme events
    - np.log1p(farm_areas) * 0.2                                # Larger farms slightly resilient
)

# Normalize
hazard_score = (hazard_score - hazard_score.mean()) / hazard_score.std()

# Generate survival times using exponential distribution
scale = 180  # Average policy duration ~180 days
lambdas = np.exp(hazard_score) / scale
simulated_time = np.random.exponential(1 / lambdas)
simulated_time = np.round(simulated_time, 0).clip(1, 730)  # 1 day to 2 years

# Administrative censoring at 365 days (end of policy period)
policy_duration = 365
claim_occurred = (simulated_time <= policy_duration).astype(int)
time_to_claim = np.minimum(simulated_time, policy_duration).astype(int)

# claim_count: number of claims in the observation period (for dataset completeness only)
# NOTE: This is EXCLUDED from model training to prevent data leakage
claim_count = np.where(claim_occurred == 1, np.random.randint(1, 4, NUM_POLICIES), 0)

# ──────────────────────────────────────────────
# 6. Introduce Missing Values (~2% per column for realism)
# ──────────────────────────────────────────────
def add_missing(arr, pct=0.02):
    """Replace ~pct fraction of values with NaN."""
    mask = np.random.random(len(arr)) < pct
    result = arr.astype(float)
    result[mask] = np.nan
    return result

# ──────────────────────────────────────────────
# 7. Assemble DataFrame
# ──────────────────────────────────────────────
df = pd.DataFrame({
    'policy_id': np.arange(1, NUM_POLICIES + 1),
    'farmer_id': [f"F{np.random.randint(1000, 9999)}" for _ in range(NUM_POLICIES)],
    'state': states,
    'district': districts,
    'latitude': np.round(latitudes, 4),
    'longitude': np.round(longitudes, 4),
    'crop_type': crop_types,
    'crop_season': crop_seasons,
    'farm_area': farm_areas,
    'soil_type': soil_types,
    'irrigation_type': irrigation_types,
    'elnino_status': elnino_statuses,
    'enso_index': enso_indices,
    'elnino_intensity': elnino_intensities,
    'normal_rainfall': normal_rainfalls,
    'rainfall': rainfalls,
    'rainfall_deviation': rainfall_deviations,
    'temperature': temperatures,
    'temperature_deviation': temperature_deviations,
    'humidity': humidities,
    'soil_moisture': soil_moistures,
    'drought_index': drought_indices,
    'flood_index': flood_indices,
    'extreme_weather_events': extreme_weather_events,
    'weather_anomaly_score': weather_anomaly_scores,
    'historical_yield': historical_yields,
    'current_yield': current_yields,
    'insurance_amount': insurance_amounts,
    'premium_amount': premium_amounts,
    'previous_claims': previous_claims,
    'claim_count': claim_count,
    'time_to_claim': time_to_claim,
    'claim_occurred': claim_occurred,
})

# Add ~2% missing values to select columns for realism
for col in ['humidity', 'soil_moisture', 'weather_anomaly_score', 'historical_yield']:
    mask = np.random.random(NUM_POLICIES) < 0.02
    df.loc[mask, col] = np.nan

# ──────────────────────────────────────────────
# 8. Save
# ──────────────────────────────────────────────
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'raw_unclean_dataset.csv')
df.to_csv(output_path, index=False)

print(f"Generated {NUM_POLICIES} records → {output_path}")
print(f"Columns: {list(df.columns)}")
print(f"Shape: {df.shape}")
print(f"Event rate (claims filed): {df['claim_occurred'].mean():.2%}")
print(f"Median time-to-claim (events only): {df.loc[df['claim_occurred']==1, 'time_to_claim'].median():.0f} days")
print(f"Censoring rate: {(1 - df['claim_occurred'].mean()):.2%}")
print(f"\nEl Niño effect check:")
print(f"  Active El Nino claim rate: {df.loc[df['elnino_status']=='Active El Nino', 'claim_occurred'].mean():.2%}")
print(f"  Neutral claim rate:        {df.loc[df['elnino_status']=='Neutral', 'claim_occurred'].mean():.2%}")
print(f"  La Nina claim rate:        {df.loc[df['elnino_status']=='La Nina', 'claim_occurred'].mean():.2%}")
