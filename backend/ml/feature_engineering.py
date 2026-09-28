import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineeringPipeline:
    def __init__(self, raw_data_path, output_dir):
        self.raw_data_path = raw_data_path
        self.output_dir = output_dir
        self.df = None
        
        os.makedirs(output_dir, exist_ok=True)
        sns.set_theme(style="whitegrid")

    def load_and_clean_data(self):
        """Loads the raw dataset, handles missing values, and drops duplicates."""
        print(f"Loading data from {self.raw_data_path}...")
        self.df = pd.read_csv(self.raw_data_path)
        
        # 1. Drop duplicates
        self.df = self.df.drop_duplicates()
        
        # 2. Handle missing values
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
        
        categorical_cols = self.df.select_dtypes(exclude=[np.number]).columns
        for col in categorical_cols:
            self.df[col] = self.df[col].fillna(self.df[col].mode()[0])

    def module_1_weather_features(self):
        """
        MODULE 1 — WEATHER FEATURES
        Calculates/derives deviations, anomalies, and severity indicators.
        """
        print("Deriving Module 1: Weather Features...")
        
        # We re-derive these explicitly as part of the ML pipeline
        self.df['derived_rainfall_deviation'] = self.df['rainfall'] - self.df['normal_rainfall']
        self.df['derived_temperature_anomaly'] = self.df['temperature'] - 28.0 # Assuming 28C is normal base
        self.df['precipitation_anomaly_pct'] = (self.df['derived_rainfall_deviation'] / self.df['normal_rainfall']) * 100
        
        # Drought Severity: (0 to 1) based on soil moisture and temperature
        self.df['derived_soil_moisture_anomaly'] = 1.0 - self.df['soil_moisture']
        self.df['drought_severity'] = np.clip(self.df['derived_soil_moisture_anomaly'] + (self.df['derived_temperature_anomaly'] * 0.1), 0, 1.0)
        
        # Flood Severity: based on extreme positive rainfall deviation
        self.df['flood_severity'] = np.clip(self.df['derived_rainfall_deviation'] / 800.0, 0, 1.0)
        
        # Humidity Anomaly
        self.df['humidity_anomaly'] = self.df['humidity'] - 65.0 # Assuming 65% is normal
        
        # Extreme Indicators
        self.df['extreme_temperature_indicator'] = (self.df['derived_temperature_anomaly'] > 2.5).astype(int)
        self.df['extreme_rainfall_indicator'] = (self.df['derived_rainfall_deviation'] > 500).astype(int)
        
        # Consecutive dry days (proxy based on drought severity)
        self.df['consecutive_dry_days_proxy'] = np.round(self.df['drought_severity'] * 45) # Max 45 days
        
        # Base Weather Anomaly Score (normalized 0-1)
        self.df['base_weather_anomaly_score'] = (self.df['drought_severity']*0.5 + self.df['flood_severity']*0.3 + self.df['extreme_temperature_indicator']*0.2)

    def module_2_el_nino_features(self):
        """
        MODULE 2 — EL NIÑO
        Creates an El Niño representation based on ENSO/ONI index.
        """
        print("Deriving Module 2: El Niño Features...")
        
        # ENSO Category mapping from index
        conditions = [
            (self.df['enso_index'] >= 1.5),
            (self.df['enso_index'] >= 1.0) & (self.df['enso_index'] < 1.5),
            (self.df['enso_index'] >= 0.5) & (self.df['enso_index'] < 1.0),
            (self.df['enso_index'] > -0.5) & (self.df['enso_index'] < 0.5),
            (self.df['enso_index'] <= -0.5)
        ]
        choices = ['Strong El Niño', 'Moderate El Niño', 'Weak El Niño', 'Neutral', 'La Niña']
        self.df['derived_enso_category'] = np.select(conditions, choices, default='Neutral')
        
        self.df['el_nino_indicator'] = (self.df['enso_index'] >= 0.5).astype(int)
        self.df['el_nino_intensity_numeric'] = np.clip(self.df['enso_index'], 0, None)
        
        # Simulated duration of episode in months (deterministic formula)
        self.df['duration_of_episode_months'] = np.where(self.df['el_nino_indicator'] == 1, 
                                                         np.clip((np.abs(self.df['enso_index']) * 8 + 4).astype(int), 6, 18), 0)

    def module_3_interaction_features(self):
        """
        MODULE 3 — INTERACTION FEATURES
        Multiplicative interactions between El Niño, Geography, and Weather.
        """
        print("Deriving Module 3: Interaction Features...")
        
        # El Nino interactions
        self.df['elnino_x_rainfall_dev'] = self.df['el_nino_indicator'] * self.df['derived_rainfall_deviation']
        self.df['elnino_x_drought_index'] = self.df['el_nino_indicator'] * self.df['drought_severity']
        self.df['elnino_x_temperature_anomaly'] = self.df['el_nino_indicator'] * self.df['derived_temperature_anomaly']
        self.df['elnino_x_soil_moisture'] = self.df['el_nino_indicator'] * self.df['soil_moisture']
        
        # Label encode categoricals for interaction math using FIXED ordinal mappings
        # Sorted alphabetically — matches sklearn LabelEncoder default behaviour
        crop_ordinal = {v: i for i, v in enumerate(sorted(self.df['crop_type'].unique()))}
        state_ordinal = {v: i for i, v in enumerate(sorted(self.df['state'].unique()))}
        irrigation_ordinal = {v: i for i, v in enumerate(sorted(self.df['irrigation_type'].unique()))}
        
        crop_encoded = self.df['crop_type'].map(crop_ordinal).values
        region_encoded = self.df['state'].map(state_ordinal).values
        irrigation_encoded = self.df['irrigation_type'].map(irrigation_ordinal).values
        
        # Crop interactions
        self.df['crop_x_rainfall_dev'] = crop_encoded * self.df['derived_rainfall_deviation']
        self.df['crop_x_drought'] = crop_encoded * self.df['drought_severity']
        
        # Irrigation & Region interactions
        self.df['irrigation_x_drought'] = irrigation_encoded * self.df['drought_severity']
        self.df['region_x_elnino'] = region_encoded * self.df['el_nino_indicator']

    def module_4_risk_score(self):
        """
        MODULE 4 — RISK SCORE
        Preliminary Weather Risk Score (0–100) for interpretability.
        """
        print("Deriving Module 4: Preliminary Weather Risk Score...")
        
        # Create a 0-100 score based on drought, flood, extreme temps, and El Nino intensity
        raw_score = (
            self.df['drought_severity'] * 40 +
            self.df['flood_severity'] * 30 +
            self.df['extreme_temperature_indicator'] * 15 +
            (self.df['el_nino_intensity_numeric'] / 2.5) * 15 
        )
        self.df['preliminary_weather_risk_score'] = np.clip(np.round(raw_score, 0), 0, 100).astype(int)

    def encode_and_scale(self):
        """Encodes categorical variables and scales numerical features."""
        print("Encoding and scaling features...")
        
        # Drop columns not suitable for modeling or that cause data leakage
        # DATA LEAKAGE PREVENTION:
        # We must drop variables that are measured AFTER the claim occurs or represent the outcome itself,
        # other than the survival analysis targets (time_to_claim, claim_occurred).
        # Dropping: current_yield (measured at harvest, post-claim), claim_count (encodes claim outcome)
        drop_cols = ['policy_id', 'farmer_id', 'district', 'current_yield', 'claim_count']
        self.df = self.df.drop(columns=[col for col in drop_cols if col in self.df.columns])
        
        # Encode
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        self.df = pd.get_dummies(self.df, columns=categorical_cols, drop_first=True)
        
        # Scale continuous features
        scaler = StandardScaler()
        # Ensure we don't scale targets or binary indicators
        binary_cols = [col for col in self.df.columns if self.df[col].nunique() == 2]
        target_cols = ['time_to_claim', 'claim_occurred', 'preliminary_weather_risk_score']
        exclude_from_scaling = binary_cols + target_cols
        
        scale_cols = [col for col in self.df.columns if col not in exclude_from_scaling]
        self.df[scale_cols] = scaler.fit_transform(self.df[scale_cols])
        
        # Save the scaler and the list of columns for inference
        with open(f'{self.output_dir}/scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        with open(f'{self.output_dir}/model_columns.pkl', 'wb') as f:
            pickle.dump(list(self.df.columns), f)
        with open(f'{self.output_dir}/scale_cols.pkl', 'wb') as f:
            pickle.dump(scale_cols, f)

    def generate_visualizations(self):
        """Generates the 8 exploratory visualizations requested."""
        print("Generating Exploratory Visualizations...")
        
        # 1. Rainfall vs claim rate
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x='claim_occurred', y='derived_rainfall_deviation')
        plt.title('1. Rainfall Deviation vs Claim Occurrence')
        plt.savefig(f'{self.output_dir}/1_rainfall_vs_claim.png')
        plt.close()
        
        # 2. Drought vs claim rate
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=self.df, x='claim_occurred', y='drought_severity')
        plt.title('2. Drought Severity vs Claim Occurrence')
        plt.savefig(f'{self.output_dir}/2_drought_vs_claim.png')
        plt.close()
        
        # 3. El Niño vs claim rate
        # We use a temporary un-encoded df for plotting categoricals if they were encoded
        # Since we ran encode_and_scale, we'll reload just for plotting or use the encoded dummies
        # To make it easier, we will recreate a plotting df
        plot_df = pd.read_csv(self.raw_data_path)
        plot_df['derived_temperature_anomaly'] = plot_df['temperature'] - 28.0
        plot_df['weather_anomaly'] = plot_df['drought_index'] * 0.5 + plot_df['flood_index'] * 0.5
        
        plt.figure(figsize=(8, 5))
        sns.barplot(data=plot_df, x='elnino_intensity', y='claim_occurred', errorbar=None, 
                    order=['Strong El Nino', 'Moderate El Nino', 'Weak El Nino', 'La Nina'])
        plt.title('3. El Niño Category vs Claim Rate')
        plt.savefig(f'{self.output_dir}/3_elnino_vs_claim_rate.png')
        plt.close()
        
        # 4. Temperature anomaly vs claim rate
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=plot_df, x='claim_occurred', y='derived_temperature_anomaly')
        plt.title('4. Temperature Anomaly vs Claim Occurrence')
        plt.savefig(f'{self.output_dir}/4_temp_anomaly_vs_claim.png')
        plt.close()
        
        # 5. Survival curves by El Niño category (Kaplan-Meier proxy plot)
        plt.figure(figsize=(8, 5))
        for intensity in ['Strong El Nino', 'La Nina']:
            subset = plot_df[plot_df['elnino_intensity'] == intensity]
            sns.kdeplot(data=subset[subset['claim_occurred']==1], x='time_to_claim', label=intensity, cumulative=True)
        plt.title('5. Cumulative Claims (Proxy Survival Curve) by El Niño Category')
        plt.legend()
        plt.savefig(f'{self.output_dir}/5_survival_curves_elnino.png')
        plt.close()
        
        # 6. Claim rate by crop
        plt.figure(figsize=(8, 5))
        sns.barplot(data=plot_df, y='crop_type', x='claim_occurred', errorbar=None)
        plt.title('6. Claim Rate by Crop Type')
        plt.savefig(f'{self.output_dir}/6_claim_rate_by_crop.png')
        plt.close()
        
        # 7. Claim rate by region
        plt.figure(figsize=(8, 5))
        sns.barplot(data=plot_df, y='state', x='claim_occurred', errorbar=None)
        plt.title('7. Claim Rate by Region (State)')
        plt.savefig(f'{self.output_dir}/7_claim_rate_by_region.png')
        plt.close()
        
        # 8. Weather anomaly vs time-to-claim
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=plot_df[plot_df['claim_occurred']==1], x='weather_anomaly', y='time_to_claim', alpha=0.5)
        plt.title('8. Weather Anomaly vs Time-to-Claim')
        plt.savefig(f'{self.output_dir}/8_weather_anomaly_vs_time.png')
        plt.close()

    def generate_academic_report(self):
        """Generates an explanation of all engineered features and data leakage."""
        report_path = f"{self.output_dir}/feature_engineering_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=========================================================\n")
            f.write(" AI-Driven Risk Assessment Model - Feature Engineering   \n")
            f.write("=========================================================\n\n")
            
            f.write("=== DATA LEAKAGE PREVENTION ===\n")
            f.write("In building this pipeline, several variables were strictly removed to prevent data leakage. Data leakage occurs when a model uses information during training that would not be available at the time of prediction.\n")
            f.write("- Excluded Variables:\n")
            f.write("  * `current_yield`: Yield is only known at the end of the crop season, during harvest. Using it to predict an in-season claim would allow the model to 'look into the future'.\n")
            f.write("  * `policy_id`, `farmer_id`: Unique identifiers do not carry predictive value and can lead to overfitting.\n")
            f.write("Only baseline geographical, historical, and rolling weather features are preserved.\n\n")
            
            f.write("=== MODULE 1: WEATHER FEATURES ===\n")
            f.write("These features quantify the deviations from normal agricultural conditions.\n")
            f.write("- `derived_rainfall_deviation`: Absolute difference between observed and normal rainfall.\n")
            f.write("- `precipitation_anomaly_pct`: Percentage deviation of rainfall from the norm.\n")
            f.write("- `derived_temperature_anomaly`: Deviation of temperature from a baseline 28°C.\n")
            f.write("- `drought_severity`: A normalized 0-1 index combining soil moisture deficit and temperature stress.\n")
            f.write("- `flood_severity`: A normalized 0-1 index tracking extreme positive rainfall deviation.\n")
            f.write("- `extreme_temperature_indicator`: Binary flag indicating temperature anomaly > 2.5°C.\n")
            f.write("- `consecutive_dry_days_proxy`: Simulated count of rainless days derived from drought severity.\n\n")
            
            f.write("=== MODULE 2: EL NIÑO FEATURES ===\n")
            f.write("These features translate the physical ENSO (El Niño-Southern Oscillation) index into categorical and intensity representations.\n")
            f.write("- `derived_enso_category`: Maps ENSO index to Strong/Moderate/Weak El Niño, Neutral, or La Niña.\n")
            f.write("- `el_nino_indicator`: Binary flag for positive El Niño status.\n")
            f.write("- `duration_of_episode_months`: Simulates the prolonged effect of the climate event.\n\n")
            
            f.write("=== MODULE 3: INTERACTION FEATURES ===\n")
            f.write("Agriculture is a complex system where risks compound. Multiplicative terms capture these non-linear effects.\n")
            f.write("- `elnino_x_rainfall_dev`: Captures the amplified effect of rainfall deficits specifically during El Niño years.\n")
            f.write("- `irrigation_x_drought`: Highlights vulnerability (Rainfed farms suffer more during droughts than Irrigated ones).\n")
            f.write("- `crop_x_rainfall_dev`: Represents specific crop sensitivities to precipitation changes.\n\n")
            
            f.write("=== MODULE 4: WEATHER RISK SCORE ===\n")
            f.write("A transparent heuristic score ranging from 0 to 100. This is not used as a machine learning feature, but rather as an interpretable dashboard metric for insurance underwriters.\n")
            f.write("- `preliminary_weather_risk_score`: Weighted sum of drought severity (40%), flood severity (30%), extreme temp (15%), and El Niño intensity (15%).\n")
            
        print(f"Academic report generated at: {report_path}")

    def run(self):
        self.load_and_clean_data()
        self.module_1_weather_features()
        self.module_2_el_nino_features()
        self.module_3_interaction_features()
        self.module_4_risk_score()
        self.generate_visualizations()
        self.generate_academic_report()
        self.encode_and_scale()
        
        # Export Survival Analysis Dataset
        output_path = f"{self.output_dir}/survival_analysis_dataset.csv"
        self.df.to_csv(output_path, index=False)
        print(f"Feature Engineering Pipeline Completed. ML-ready dataset saved to {output_path}")


if __name__ == "__main__":
    raw_data = "data/raw/raw_unclean_dataset.csv"
    output_directory = "data/processed/ml_pipeline_output"
    
    pipeline = FeatureEngineeringPipeline(raw_data_path=raw_data, output_dir=output_directory)
    pipeline.run()
