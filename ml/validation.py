import pandas as pd
import json

def generate_preprocessing_report(df_raw_dict: dict, df_final: pd.DataFrame, output_path: str = None) -> dict:
    """
    Generate a detailed report of the preprocessing pipeline.
    df_raw_dict: Dictionary containing original raw DataFrames 
                 (e.g., {'weather': df_weather, 'policies': df_policies})
    df_final: The final Survival Analysis dataset.
    """
    report = {
        "raw_data_summary": {},
        "final_dataset_summary": {},
        "survival_metrics": {}
    }
    
    # Raw stats
    for name, df in df_raw_dict.items():
        report["raw_data_summary"][name] = {
            "num_records": len(df),
            "missing_values": int(df.isna().sum().sum())
        }
        
    # Final stats
    report["final_dataset_summary"] = {
        "num_records": len(df_final),
        "missing_values": int(df_final.isna().sum().sum()),
        "features": list(df_final.columns)
    }
    
    # Survival specific stats
    if 'event' in df_final.columns:
        total_events = int(df_final['event'].sum())
        total_records = len(df_final)
        report["survival_metrics"] = {
            "total_claims_observed": total_events,
            "total_censored_observed": total_records - total_events,
            "censoring_percentage": round(((total_records - total_events) / total_records) * 100, 2) if total_records > 0 else 0
        }
        
    if 'primary_enso_phase' in df_final.columns:
        enso_counts = df_final['primary_enso_phase'].value_counts().to_dict()
        report["survival_metrics"]["enso_distribution"] = {k: int(v) for k, v in enso_counts.items()}
        
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=4)
            
    return report

def validate_no_leakage(df_final: pd.DataFrame) -> bool:
    """
    Verify that there are no obvious signs of data leakage.
    (e.g. claim_amount should not be used as a predictor)
    """
    leakage_columns = ['claim_amount', 'claim_status', 'claim_reason', 'date_of_loss']
    
    for col in leakage_columns:
        if col in df_final.columns:
            print(f"WARNING: Potential data leakage detected. Column '{col}' is in the final dataset.")
            return False
            
    # Also verify duration > 0
    if (df_final['duration'] <= 0).any():
        print("WARNING: Negative or zero duration found.")
        return False
        
    return True
