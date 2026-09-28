import pandas as pd
from lifelines import CoxPHFitter
from typing import Dict, Any, Tuple
import io

def train_cox_model(df: pd.DataFrame, duration_col: str = 'duration', event_col: str = 'event', penalizer: float = 0.01) -> Tuple[CoxPHFitter, Dict[str, Any]]:
    """
    Train a Cox Proportional Hazards model.
    Note: Categorical columns in df must be one-hot encoded (pd.get_dummies) before passing here.
    """
    # Ensure there are no NaNs in the training set
    df_train = df.dropna().copy()
    
    # We must cast booleans to floats for lifelines
    for col in df_train.columns:
        if df_train[col].dtype == bool:
            df_train[col] = df_train[col].astype(float)
            
    cph = CoxPHFitter(penalizer=penalizer)
    
    # Fit the model
    cph.fit(df_train, duration_col=duration_col, event_col=event_col)
    
    # Extract summary
    summary_df = cph.summary
    
    results = {
        "concordance_index": getattr(cph, 'concordance_index_', None),
        "log_likelihood_ratio_test": getattr(cph, 'log_likelihood_ratio_test_', None),
        "coefficients": summary_df['coef'].to_dict(),
        "hazard_ratios": summary_df['exp(coef)'].to_dict(),
        "p_values": summary_df['p'].to_dict(),
        "lower_ci_95": summary_df['exp(coef) lower 95%'].to_dict(),
        "upper_ci_95": summary_df['exp(coef) upper 95%'].to_dict()
    }
    
    return cph, results

def check_proportional_hazards_assumption(cph: CoxPHFitter, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Check the Proportional Hazards assumption using Schoenfeld residuals.
    Returns a string output of the summary and a boolean indicating if it appears reasonable.
    """
    # Lifelines check_assumptions prints to stdout, we can capture it or use compute_residuals
    # Here we just use proportional_hazard_test
    try:
        from lifelines.statistics import proportional_hazard_test
        results = proportional_hazard_test(cph, df, time_transform='rank')
        
        # If p-value < 0.05 for global or individual, assumption may be violated
        p_values = results.p_value
        is_reasonable = True
        violated_features = []
        
        for feature, p_val in p_values.items():
            if p_val < 0.05:
                is_reasonable = False
                violated_features.append(feature)
                
        return {
            "is_reasonable": is_reasonable,
            "violated_features": violated_features,
            "message": "Proportional hazards assumption appears reasonable." if is_reasonable else f"Violated by: {violated_features}"
        }
    except Exception as e:
        return {
            "is_reasonable": None,
            "violated_features": [],
            "message": f"Could not check assumptions: {str(e)}"
        }
