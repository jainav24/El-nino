import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

def train_rsf_model(df: pd.DataFrame, duration_col: str = 'duration', event_col: str = 'event', n_estimators: int = 100) -> Tuple[Any, Dict[str, Any]]:
    """
    Train a Random Survival Forest model using scikit-survival.
    Returns (model, results_dict) or (None, error_msg) if not available.
    """
    try:
        from sksurv.ensemble import RandomSurvivalForest
        from sksurv.util import Surv
    except ImportError:
        return None, {"error": "scikit-survival is not installed. Random Survival Forest cannot be trained."}
        
    df_train = df.dropna().copy()
    
    # Ensure boolean columns are floats
    for col in df_train.columns:
        if df_train[col].dtype == bool:
            df_train[col] = df_train[col].astype(float)
            
    # scikit-survival requires a structured array for the target (event, duration)
    # where event is boolean.
    
    X = df_train.drop(columns=[duration_col, event_col])
    
    events = df_train[event_col].astype(bool).values
    durations = df_train[duration_col].values
    
    y = Surv.from_arrays(event=events, time=durations)
    
    rsf = RandomSurvivalForest(n_estimators=n_estimators, min_samples_split=10, min_samples_leaf=15, n_jobs=-1, random_state=42)
    rsf.fit(X, y)
    
    c_index = rsf.score(X, y)
    
    # Feature importances are tricky to get cheaply in RSF without permutation,
    # we will just return the c-index for now as a baseline comparison.
    
    results = {
        "concordance_index": c_index,
        "n_estimators": n_estimators
    }
    
    return rsf, results
