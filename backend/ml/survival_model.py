import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
import warnings

warnings.filterwarnings('ignore')

class SurvivalAnalysisPipeline:
    def __init__(self, data_path, output_dir):
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        self.kmf = KaplanMeierFitter()
        self.cph_baseline = CoxPHFitter(penalizer=0.01) # Small penalizer for convergence stability
        self.cph_proposed = CoxPHFitter(penalizer=0.01)
        
        os.makedirs(self.output_dir, exist_ok=True)
        sns.set_theme(style="whitegrid")

    def load_data(self):
        print(f"Loading ML-ready dataset from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)
        print(f"Dataset shape: {self.df.shape}")
        
    def kaplan_meier_analysis(self):
        print("\n--- 1. Kaplan-Meier Analysis ---")
        
        T = self.df['time_to_claim']
        E = self.df['claim_occurred']
        
        # Overall Kaplan-Meier
        self.kmf.fit(T, event_observed=E, label='Overall Survival (No Claim)')
        plt.figure(figsize=(10, 6))
        self.kmf.plot_survival_function()
        plt.title('Overall Kaplan-Meier Survival Curve')
        plt.xlabel('Days (Time-to-Claim)')
        plt.ylabel('Probability of No Claim')
        plt.savefig(f'{self.output_dir}/km_overall.png')
        plt.close()
        
        # Stratified by El Nino Intensity (Since data is one-hot encoded, we reconstruct a categorical for plotting)
        plt.figure(figsize=(10, 6))
        ax = plt.subplot(111)
        
        # Assuming we have these columns from OHE: 
        # derived_enso_category_Moderate El Niño, derived_enso_category_Neutral, derived_enso_category_Strong El Niño, derived_enso_category_Weak El Niño
        categories = ['Neutral', 'Strong El Niño', 'La Niña']
        
        for cat in categories:
            col_name = f'derived_enso_category_{cat}'
            if col_name in self.df.columns:
                mask = self.df[col_name] > 0
            elif cat == 'Neutral' and 'derived_enso_category_Neutral' not in self.df.columns:
                # If Neutral was the dropped base column, it means all other category columns are 0
                other_cols = [c for c in self.df.columns if c.startswith('derived_enso_category_')]
                if len(other_cols) > 0:
                    mask = (self.df[other_cols] <= 0).all(axis=1)
                else:
                    mask = pd.Series([True]*len(self.df))
            else:
                continue
                
            if mask.sum() > 0:
                self.kmf.fit(T[mask], event_observed=E[mask], label=cat)
                self.kmf.plot_survival_function(ax=ax)
                
        plt.title('Kaplan-Meier Survival Curves Stratified by El Niño Category')
        plt.xlabel('Days')
        plt.ylabel('Survival Probability (No Claim)')
        plt.savefig(f'{self.output_dir}/km_stratified_elnino.png')
        plt.close()
        print("Kaplan-Meier curves generated.")

    def run_cox_models(self):
        print("\n--- 2. Cox Proportional Hazards (CPH) Modeling ---")
        
        # Define baseline features (Weather + Ag, NO El Nino or interactions)
        # We exclude elnino columns and interactions
        elnino_cols = [c for c in self.df.columns if 'elnino' in c.lower() or 'enso' in c.lower() or 'el_nino' in c.lower()]
        
        baseline_features = [c for c in self.df.columns if c not in elnino_cols and c not in ['time_to_claim', 'claim_occurred', 'preliminary_weather_risk_score']]
        
        df_baseline = self.df[baseline_features + ['time_to_claim', 'claim_occurred']]
        
        print("Training Baseline Model (No El Niño features)...")
        # Step size to handle convergence issues in synthetic data
        self.cph_baseline.fit(df_baseline, duration_col='time_to_claim', event_col='claim_occurred')
        c_index_baseline = self.cph_baseline.concordance_index_
        print(f"Baseline Concordance Index: {c_index_baseline:.4f}")
        
        # Define proposed features (Baseline + El Nino + Interactions)
        # Drop only the risk score which is a post-calculated heuristic
        proposed_features = [c for c in self.df.columns if c != 'preliminary_weather_risk_score']
        df_proposed = self.df[proposed_features]
        
        print("Training Proposed Model (With El Niño & Interaction features)...")
        self.cph_proposed.fit(df_proposed, duration_col='time_to_claim', event_col='claim_occurred')
        c_index_proposed = self.cph_proposed.concordance_index_
        print(f"Proposed Concordance Index: {c_index_proposed:.4f}")
        
        # Save evaluation report
        with open(f'{self.output_dir}/cph_evaluation_report.txt', 'w', encoding='utf-8') as f:
            f.write("=========================================================\n")
            f.write(" Survival Analysis Model Evaluation (CPH)\n")
            f.write("=========================================================\n\n")
            f.write(f"Baseline Model C-Index (Without El Niño): {c_index_baseline:.4f}\n")
            f.write(f"Proposed Model C-Index (With El Niño):    {c_index_proposed:.4f}\n\n")
            
            f.write("--- Hypothesis Validation ---\n")
            if c_index_proposed > c_index_baseline:
                f.write("Result: The integration of El Niño and interaction features successfully improved the predictive power of the model.\n")
            else:
                f.write("Result: The El Niño features did not improve the concordance index in this synthetic sample.\n")
                
            f.write("\n\n--- Top 10 Most Significant Hazard Ratios ---\n")
            summary = self.cph_proposed.summary
            summary = summary.sort_values(by='p', ascending=True).head(10)
            f.write(summary[['coef', 'exp(coef)', 'p', 'se(coef)']].to_string())
            
        print("Model evaluation report saved.")

    def explainability_analysis(self):
        print("\n--- 3. Explainable Risk Engine (Hazard Ratios) ---")
        
        # Plot top hazard ratios
        summary = self.cph_proposed.summary
        # Filter out intercept/small effects to focus on main drivers
        summary['abs_coef'] = np.abs(summary['coef'])
        top_features = summary.sort_values(by='abs_coef', ascending=False).head(15)
        
        plt.figure(figsize=(12, 8))
        self.cph_proposed.plot(top_features.index.tolist())
        plt.title("Cox Proportional Hazards - Top 15 Feature Importances (Log Hazard Ratios)")
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/cph_hazard_ratios.png')
        plt.close()
        print("Hazard Ratios plot saved.")

    def export_models(self):
        print("\n--- 4. Exporting Trained Models ---")
        with open(f'{self.output_dir}/cph_baseline_model.pkl', 'wb') as f:
            pickle.dump(self.cph_baseline, f)
            
        with open(f'{self.output_dir}/cph_proposed_model.pkl', 'wb') as f:
            pickle.dump(self.cph_proposed, f)
            
        print(f"Models exported to {self.output_dir}")

    def run(self):
        self.load_data()
        self.kaplan_meier_analysis()
        self.run_cox_models()
        self.explainability_analysis()
        self.export_models()
        print("\nSurvival Analysis ML Module completed successfully.")

if __name__ == "__main__":
    data_path = "data/processed/ml_pipeline_output/survival_analysis_dataset.csv"
    output_directory = "data/processed/model_output"
        
    pipeline = SurvivalAnalysisPipeline(data_path=data_path, output_dir=output_directory)
    pipeline.run()
