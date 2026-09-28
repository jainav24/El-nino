import pandas as pd
import os
import joblib
from typing import Dict, Any

from ml.training.kaplan_meier import generate_kaplan_meier
from ml.training.cox_model import train_cox_model, check_proportional_hazards_assumption
from ml.training.rsf_model import train_rsf_model
from ml.evaluation.metrics import evaluate_model
from ml.config import CATEGORICAL_COLUMNS

def train_survival_model(df_train: pd.DataFrame, df_test: pd.DataFrame = None, models_dir: str = 'ml/models') -> Dict[str, Any]:
    """
    Orchestrates the training of survival models (Cox PH, and optionally RSF).
    Handles dummy encoding and artifact generation.
    """
    
    # Ensure models directory exists
    os.makedirs(models_dir, exist_ok=True)
    
    report = {}
    
    # One-hot encode categorical columns
    cols_to_encode = [col for col in CATEGORICAL_COLUMNS if col in df_train.columns]
    
    df_train_encoded = pd.get_dummies(df_train, columns=cols_to_encode, drop_first=True)
    
    # Save the dummy columns so we can align inference data later
    expected_columns = list(df_train_encoded.columns)
    joblib.dump(expected_columns, os.path.join(models_dir, 'expected_columns.joblib'))
    
    if df_test is not None:
        df_test_encoded = pd.get_dummies(df_test, columns=cols_to_encode, drop_first=True)
        # Align columns
        df_test_encoded = df_test_encoded.reindex(columns=expected_columns, fill_value=0)
    else:
        df_test_encoded = df_train_encoded # fallback to train eval
        
    # 1. Train Cox Model
    cph_model, cox_results = train_cox_model(df_train_encoded)
    
    # Diagnostics
    assumption_check = check_proportional_hazards_assumption(cph_model, df_train_encoded)
    cox_results['proportional_hazards_assumption'] = assumption_check
    
    # Evaluation
    eval_results = evaluate_model(cph_model, df_test_encoded)
    cox_results['test_evaluation'] = eval_results
    
    report['cox_model'] = cox_results
    
    # Save Model
    # Since lifelines models are just standard python objects containing arrays, we can pickle them.
    # We use joblib for efficiency.
    joblib.dump(cph_model, os.path.join(models_dir, 'cox_ph_model.joblib'))
    
    # 2. Train Random Survival Forest (Optional)
    rsf_model, rsf_results = train_rsf_model(df_train_encoded)
    report['rsf_model'] = rsf_results
    
    if rsf_model:
        joblib.dump(rsf_model, os.path.join(models_dir, 'rsf_model.joblib'))
        
    return report
