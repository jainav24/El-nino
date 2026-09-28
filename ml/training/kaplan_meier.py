import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from typing import Dict, Any, Tuple

def generate_kaplan_meier(df: pd.DataFrame, group_col: str = None, duration_col: str = 'duration', event_col: str = 'event') -> Dict[str, Any]:
    """
    Generate Kaplan-Meier survival curves.
    If group_col is provided, computes separate curves for each group.
    
    Returns a dictionary containing for each group:
    - survival_probability (dict mapping time -> prob)
    - cumulative_event_probability (1 - survival_probability)
    - number_at_risk (dict mapping time -> count)
    - median_survival_time (float or None)
    """
    results = {}
    
    if group_col and group_col in df.columns:
        groups = df[group_col].unique()
        for group in groups:
            mask = (df[group_col] == group)
            T = df[mask][duration_col]
            E = df[mask][event_col]
            
            kmf = KaplanMeierFitter()
            kmf.fit(T, event_observed=E, label=str(group))
            
            results[str(group)] = _extract_kmf_metrics(kmf)
    else:
        T = df[duration_col]
        E = df[event_col]
        
        kmf = KaplanMeierFitter()
        kmf.fit(T, event_observed=E, label='All')
        results['All'] = _extract_kmf_metrics(kmf)
        
    return results

def _extract_kmf_metrics(kmf: KaplanMeierFitter) -> Dict[str, Any]:
    survival_table = kmf.event_table
    timeline = survival_table.index.tolist()
    
    # Survival Probabilities
    surv_probs = kmf.survival_function_[kmf._label].to_dict()
    
    # Cumulative Events (1 - Survival)
    cum_probs = {t: 1.0 - p for t, p in surv_probs.items()}
    
    # Number at risk at each time point
    at_risk = survival_table['at_risk'].to_dict()
    
    med_surv_time = getattr(kmf, 'median_survival_time_', None)
    if med_surv_time is not None and np.isinf(med_surv_time):
        med_surv_time = None
        
    return {
        "median_survival_time": med_surv_time,
        "survival_probability": surv_probs,
        "cumulative_event_probability": cum_probs,
        "number_at_risk": at_risk
    }
