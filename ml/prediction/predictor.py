import pandas as pd
import numpy as np
from lifelines import CoxPHFitter
from typing import Dict, Any, List

def predict_survival(cph: CoxPHFitter, X: pd.DataFrame, times: List[int]) -> Dict[str, float]:
    """
    Predict survival probability at specific times (days).
    """
    # Ensure times are sorted
    times = sorted(times)
    
    # Predict survival function for the new observations
    # Returns a DataFrame where rows are times and columns are observation index
    surv_func = cph.predict_survival_function(X, times=times)
    
    # For a single observation, format it nicely
    if len(X) == 1:
        probs = surv_func.iloc[:, 0].to_dict()
        return {f"{int(t)}_days": round(float(p), 4) for t, p in probs.items()}
        
    return surv_func.to_dict()

def calculate_hazard(cph: CoxPHFitter, X: pd.DataFrame) -> float:
    """
    Calculate the relative hazard (partial hazard) for an observation.
    """
    # predict_partial_hazard returns the exp(X * beta)
    hazards = cph.predict_partial_hazard(X)
    
    if len(X) == 1:
        return float(hazards.iloc[0])
    return hazards.tolist()

def calculate_risk_category(hazard_ratio: float) -> str:
    """
    Categorize risk based on relative hazard ratio.
    """
    if hazard_ratio < 0.8:
        return "Low"
    elif hazard_ratio <= 1.2:
        return "Medium"
    elif hazard_ratio <= 2.0:
        return "High"
    else:
        return "Critical"
