import pandas as pd
import numpy as np
import os
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

def set_seed(seed=42):
    np.random.seed(seed)

def generate_synthetic_data(num_rows):
    set_seed(42)
    
    # Categorical options
    states = ['Maharashtra', 'Karnataka', 'Madhya Pradesh', 'Punjab', 'Uttar Pradesh', 'Andhra Pradesh']
    crop_types = ['Rice', 'Wheat', 'Maize', 'Soybean', 'Cotton', 'Sugarcane']
    crop_seasons = ['Kharif', 'Rabi', 'Zaid']
    soil_types = ['Black', 'Alluvial', 'Red', 'Laterite', 'Loamy']
    irrigation_types = ['Rainfed', 'Canal', 'Tube Well', 'Drip']
    elnino_intensities = ['None', 'Weak El Niño', 'Moderate El Niño', 'Strong El Niño', 'La Niña']
    
    data = {}
    
    # 1. Base Identifiers & Geography
    data['policy_id'] = [f"POL{str(i).zfill(7)}" for i in range(1, num_rows + 1)]
    data['farmer_id'] = [f"FMR{str(np.random.randint(1, num_rows//2)).zfill(5)}" for _ in range(num_rows)]
    data['state'] = np.random.choice(states, num_rows, p=[0.25, 0.2, 0.15, 0.15, 0.15, 0.1])
    data['district'] = [f"{s}_Dist_{np.random.randint(1, 15)}" for s in data['state']]
    data['latitude'] = np.random.uniform(12.0, 32.0, num_rows)
    data['longitude'] = np.random.uniform(72.0, 85.0, num_rows)
    
    # 2. Crop & Farm Features
    data['crop_type'] = np.random.choice(crop_types, num_rows)
    # Realistic season mapping logic approximation
    data['crop_season'] = np.where(np.isin(data['crop_type'], ['Rice', 'Cotton', 'Soybean']), 
                                   np.random.choice(['Kharif'], num_rows),
                                   np.where(np.isin(data['crop_type'], ['Wheat']), 'Rabi',
                                            np.random.choice(crop_seasons, num_rows)))
    data['farm_area'] = np.round(np.random.lognormal(mean=1.0, sigma=0.8, size=num_rows), 2)
    data['soil_type'] = np.random.choice(soil_types, num_rows)
    data['irrigation_type'] = np.random.choice(irrigation_types, num_rows, p=[0.45, 0.25, 0.2, 0.1])
    
    # 3. El Nino Features
    data['elnino_status'] = np.random.choice(['Neutral', 'Active El Nino', 'La Nina'], num_rows, p=[0.4, 0.4, 0.2])
    
    enso_idx = []
    intensity = []
    for status in data['elnino_status']:
        if status == 'Active El Nino':
            val = np.random.uniform(0.5, 2.5)
            if val > 1.5:
                intensity.append('Strong El Nino')
            elif val > 1.0:
                intensity.append('Moderate El Nino')
            else:
                intensity.append('Weak El Nino')
        elif status == 'La Nina':
            val = np.random.uniform(-2.5, -0.5)
            intensity.append('La Nina')
        else:
            val = np.random.uniform(-0.49, 0.49)
            intensity.append('None')
        enso_idx.append(val)
        
    data['enso_index'] = np.round(enso_idx, 2)
    data['elnino_intensity'] = intensity
    
    # 4. Weather Features
    # Normal rainfall depends on season and region (approximate)
    base_rain = np.where(data['crop_season'] == 'Kharif', 800, 
                 np.where(data['crop_season'] == 'Rabi', 150, 100))
    data['normal_rainfall'] = np.random.normal(base_rain, base_rain*0.1)
    
    # El Niño impacts rainfall differently: typically reduces rainfall in Kharif, sometimes increases in Rabi
    rain_modifier = np.ones(num_rows)
    # Drought effect from El Nino
    mask_strong = np.array(data['elnino_intensity']) == 'Strong El Niño'
    mask_moderate = np.array(data['elnino_intensity']) == 'Moderate El Niño'
    mask_lanina = np.array(data['elnino_intensity']) == 'La Niña'
    
    rain_modifier[mask_strong] = np.random.uniform(0.4, 0.7, mask_strong.sum())
    rain_modifier[mask_moderate] = np.random.uniform(0.6, 0.9, mask_moderate.sum())
    rain_modifier[mask_lanina] = np.random.uniform(1.1, 1.5, mask_lanina.sum())
    
    data['rainfall'] = np.round(data['normal_rainfall'] * rain_modifier, 1)
    data['rainfall_deviation'] = np.round(data['rainfall'] - data['normal_rainfall'], 1)
    
    # Temperature (El Nino generally means warmer)
    base_temp = 28.0
    temp_modifier = np.zeros(num_rows)
    temp_modifier[mask_strong] = np.random.normal(2.5, 0.5, mask_strong.sum())
    temp_modifier[mask_moderate] = np.random.normal(1.2, 0.4, mask_moderate.sum())
    temp_modifier[mask_lanina] = np.random.normal(-1.0, 0.5, mask_lanina.sum())
    
    data['temperature'] = np.round(base_temp + temp_modifier + np.random.normal(0, 1.0, num_rows), 1)
    data['temperature_deviation'] = np.round(data['temperature'] - base_temp, 1)
    
    # Derived Indices
    data['humidity'] = np.clip(np.random.normal(65, 15, num_rows) + (data['rainfall_deviation']*0.05), 10, 100)
    
    # Soil moisture drops heavily with negative rainfall deviation and high temp, offset by irrigation
    irrigation_bonus = np.where(data['irrigation_type'] == 'Canal', 0.3,
                                np.where(data['irrigation_type'] == 'Tube Well', 0.2,
                                         np.where(data['irrigation_type'] == 'Drip', 0.4, 0.0)))
    
    moisture_base = (data['rainfall'] / data['normal_rainfall']) * 0.5
    data['soil_moisture'] = np.clip(moisture_base - (data['temperature_deviation'] * 0.05) + irrigation_bonus, 0.05, 1.0)
    
    data['drought_index'] = np.clip(1.0 - data['soil_moisture'], 0, 1.0)
    data['flood_index'] = np.clip(data['rainfall_deviation'] / 800, 0, 1.0)
    
    data['extreme_weather_events'] = np.where((data['drought_index'] > 0.7) | (data['flood_index'] > 0.5) | (data['temperature_deviation'] > 2.0), 
                                              np.random.randint(1, 4, num_rows), 0)
                                              
    data['weather_anomaly_score'] = np.round((data['drought_index'] * 0.5) + (data['flood_index'] * 0.3) + (data['extreme_weather_events'] * 0.2), 2)
    
    # 5. Yield & Insurance Features
    data['historical_yield'] = np.round(np.random.normal(3500, 800, num_rows) * data['farm_area'], 0)
    yield_drop = np.clip(1.0 - (data['weather_anomaly_score'] * np.random.uniform(0.3, 0.8, num_rows)), 0.1, 1.0)
    data['current_yield'] = np.round(data['historical_yield'] * yield_drop, 0)
    
    data['insurance_amount'] = np.round(data['farm_area'] * np.random.uniform(15000, 40000, num_rows), 0)
    data['premium_amount'] = np.round(data['insurance_amount'] * np.random.uniform(0.02, 0.08, num_rows), 0)
    
    data['previous_claims'] = np.random.choice([0, 1, 2, 3, 4], num_rows, p=[0.6, 0.25, 0.1, 0.04, 0.01])
    data['claim_count'] = data['previous_claims'] 
    
    df = pd.DataFrame(data)
    
    # 6. Survival Analysis Formulation: `duration` and `event`
    max_duration = np.where(df['crop_season'] == 'Kharif', 150,
                            np.where(df['crop_season'] == 'Rabi', 120, 90))
                            
    # Hazard connects weather anomalies, poor irrigation, past claims to failure risk
    hazard = (
        df['drought_index'] * 3.5 +
        df['flood_index'] * 2.5 +
        (df['irrigation_type'] == 'Rainfed').astype(int) * 1.5 +
        df['previous_claims'] * 0.5 +
        df['temperature_deviation'] * 0.2
    )
    # Exponentiate to get lambda for exponential distribution
    hazard_rate = np.exp((hazard - hazard.mean()) / hazard.std()) / 120.0
    
    simulated_time = np.random.exponential(1.0 / hazard_rate)
    
    # time_to_claim (duration)
    df['time_to_claim'] = np.round(np.minimum(simulated_time, max_duration), 0)
    # claim_occurred (event)
    df['claim_occurred'] = (simulated_time <= max_duration).astype(int)
    
    return df

def simulate_real_world_issues(df):
    """Introduces missing values, outliers, and duplicates to simulate dirty data."""
    # 1. Missing Values
    print("Introducing missing values...")
    cols_to_null = ['soil_moisture', 'humidity', 'temperature']
    for col in cols_to_null:
        mask = np.random.rand(len(df)) < 0.05
        df.loc[mask, col] = np.nan
        
    # 2. Outliers (Extreme unrealistic temperatures due to sensor errors)
    print("Introducing outliers...")
    outlier_idx = np.random.choice(df.index, size=50, replace=False)
    df.loc[outlier_idx, 'temperature'] = np.random.uniform(60, 100, 50)
    
    # 3. Duplicates
    print("Introducing duplicates...")
    duplicates = df.sample(n=100, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df

def validate_and_clean_data(df):
    """Pipeline for cleaning and validating the data."""
    print("\n--- Data Validation & Cleaning ---")
    
    # 1. Duplicate Detection
    duplicates = df.duplicated().sum()
    print(f"Duplicates found: {duplicates}")
    if duplicates > 0:
        df = df.drop_duplicates()
        
    # 2. Missing Value Handling
    missing_before = df.isnull().sum().sum()
    for col in df.columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
    print(f"Missing values imputed: {missing_before}")
    
    # 3. Outlier Detection
    Q1 = df['temperature'].quantile(0.25)
    Q3 = df['temperature'].quantile(0.75)
    IQR = Q3 - Q1
    outliers_temp = df[(df['temperature'] < (Q1 - 1.5 * IQR)) | (df['temperature'] > (Q3 + 1.5 * IQR))]
    print(f"Outliers detected in temperature (IQR method): {len(outliers_temp)}")
    # Cap extreme temperatures to reasonable max (e.g. 50C)
    df['temperature'] = np.where(df['temperature'] > 55.0, 55.0, df['temperature'])
    
    # 4. Data Type Validation
    df['time_to_claim'] = df['time_to_claim'].astype(int)
    df['claim_occurred'] = df['claim_occurred'].astype(int)
    df['claim_count'] = df['claim_count'].astype(int)
    print("Data types validated.")
    
    return df

def generate_visualizations(df, output_dir):
    """Generates charts for EDA."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Generating Visualizations in {output_dir} ---")
    
    sns.set_theme(style="whitegrid")
    
    # 1. Claim Distribution
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x='claim_occurred', palette='Set2')
    plt.title('Distribution of Claims Occurred')
    plt.savefig(f'{output_dir}/1_claim_distribution.png', bbox_inches='tight')
    plt.close()
    
    # 2. Crop Distribution
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, y='crop_type', order=df['crop_type'].value_counts().index, palette='viridis')
    plt.title('Distribution of Crop Types')
    plt.savefig(f'{output_dir}/2_crop_distribution.png', bbox_inches='tight')
    plt.close()
    
    # 3. Rainfall Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x='rainfall', hue='elnino_status', bins=30, kde=True)
    plt.title('Rainfall Distribution by El Niño Status')
    plt.savefig(f'{output_dir}/3_rainfall_distribution.png', bbox_inches='tight')
    plt.close()
    
    # 4. Temperature Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x='temperature', hue='elnino_status', bins=30, kde=True)
    plt.title('Temperature Distribution by El Niño Status')
    plt.savefig(f'{output_dir}/4_temperature_distribution.png', bbox_inches='tight')
    plt.close()
    
    # 5. El Niño Distribution
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, x='elnino_intensity', order=['Strong El Niño', 'Moderate El Niño', 'Weak El Niño', 'None', 'La Niña'], palette='coolwarm_r')
    plt.title('Distribution of El Niño Intensities')
    plt.savefig(f'{output_dir}/5_elnino_distribution.png', bbox_inches='tight')
    plt.close()
    
    # 6. Risk Factors (Correlation)
    plt.figure(figsize=(10, 8))
    cols_corr = ['drought_index', 'flood_index', 'temperature_deviation', 'soil_moisture', 'weather_anomaly_score', 'claim_occurred']
    sns.heatmap(df[cols_corr].corr(), annot=True, cmap='RdYlGn_r', fmt=".2f")
    plt.title('Correlation Matrix of Risk Factors')
    plt.savefig(f'{output_dir}/6_risk_factors_corr.png', bbox_inches='tight')
    plt.close()
    
    # 7. Time-to-Claim Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df[df['claim_occurred'] == 1], x='time_to_claim', bins=30, kde=True, color='indianred')
    plt.title('Time to Claim Distribution (For Claimed Policies)')
    plt.savefig(f'{output_dir}/7_time_to_claim_dist.png', bbox_inches='tight')
    plt.close()

def export_and_split(df, output_dir):
    """Splits into train/test and exports CSVs."""
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(f'{output_dir}/full_dataset.csv', index=False)
    
    train, test = train_test_split(df, test_size=0.2, random_state=42, stratify=df['claim_occurred'])
    train.to_csv(f'{output_dir}/train_dataset.csv', index=False)
    test.to_csv(f'{output_dir}/test_dataset.csv', index=False)
    
    print(f"\n--- Data Exported ---")
    print(f"Full dataset saved: {len(df)} rows")
    print(f"Train dataset saved: {len(train)} rows")
    print(f"Test dataset saved: {len(test)} rows")

def generate_report(df, output_dir):
    """Generates a text report explaining variables and limitations."""
    report_path = f"{output_dir}/dataset_summary_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=========================================================\n")
        f.write(" AI-Driven Risk Assessment Model - Dataset Summary Report\n")
        f.write("=========================================================\n\n")
        
        f.write(f"Total Records Generated: {len(df)}\n")
        f.write(f"Overall Claim Rate: {df['claim_occurred'].mean():.2%}\n\n")
        
        f.write("=== Target Variables for Survival Analysis ===\n")
        f.write("1. duration (`time_to_claim`): The number of days from the start of the crop season until a claim is filed. If no claim is filed, it is the total duration of the crop season.\n")
        f.write("2. event (`claim_occurred`): Binary indicator (1 if a claim was filed, 0 if the policy ended without a claim, representing right-censored data).\n")
        f.write("   - Construction: We compute a hazard rate combining drought severity, flood severity, poor irrigation, and temperature deviations. Using this hazard rate, an exponential distribution simulates 'time_to_failure'. If this time is less than the crop season's maximum duration, an event (claim) occurs.\n\n")
        
        f.write("=== Feature Engineering Context ===\n")
        f.write("Variables like `rainfall_deviation`, `drought_index`, and `weather_anomaly_score` are included to establish ground-truth causal relationships in this synthetic environment. In the ML pipeline, these will be treated as derived features from the raw telemetry (rainfall, temperature).\n\n")
        
        f.write("=== Summary Statistics of Key Variables ===\n")
        f.write(str(df[['rainfall', 'temperature', 'drought_index', 'time_to_claim']].describe()))
        f.write("\n\n")
        
        f.write("=== Synthetic Data Limitations (For Academic Disclosure) ===\n")
        f.write("To ensure academic integrity, the following limitations must be disclosed in the project report:\n")
        f.write("1. Synthetic Causality: The relationships between El Niño, weather anomalies, and crop failure are heuristically programmed via a defined hazard function, rather than empirically derived from true historical actuarial loss tables.\n")
        f.write("2. Lack of Micro-climates: Weather features are modeled at a generalized distribution level without complex spatial auto-correlation (e.g., adjacent farms experiencing identical local floods).\n")
        f.write("3. Temporal Independence: Each row acts as an independent policy without longitudinal farmer history, missing the true year-over-year temporal dynamics of agricultural risk.\n")
    print(f"\nSummary report generated at: {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Synthetic Agricultural Insurance Dataset")
    parser.add_argument("--rows", type=int, default=10000, help="Number of rows to generate")
    args = parser.parse_args()
    
    print(f"Generating synthetic dataset with {args.rows} rows...")
    df_raw = generate_synthetic_data(args.rows)
    df_dirty = simulate_real_world_issues(df_raw)
    
    # Save raw dataset
    raw_dir = "data/raw"
    processed_dir = "data/processed"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    raw_path = f"{raw_dir}/raw_unclean_dataset.csv"
    df_dirty.to_csv(raw_path, index=False)
    print(f"Raw dirty dataset saved to {raw_path}")
    
    # Clean and validate
    df_clean = validate_and_clean_data(df_dirty)
    
    # Save processed, splits and reports
    export_and_split(df_clean, processed_dir)
    generate_visualizations(df_clean, processed_dir)
    generate_report(df_clean, processed_dir)
    print("\nDataset pipeline completed successfully.")
