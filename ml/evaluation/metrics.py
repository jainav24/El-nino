from lifelines import CoxPHFitter
import numpy as np
import pandas as pd
from typing import Dict, Any

def evaluate_model(cph: CoxPHFitter, df_test: pd.DataFrame, duration_col: str = 'duration', event_col: str = 'event') -> Dict[str, Any]:
    """
    Evaluate the Cox Proportional Hazards model.
    """
    results = {}
    
    # Concordance Index (C-index)
    c_index = cph.score(df_test, scoring_method="concordance_index")
    results['concordance_index'] = c_index
    
    # We can calculate prediction error or Brier score manually if needed, 
    # but lifelines provides the C-index natively which is standard for survival models.
    
    return results
