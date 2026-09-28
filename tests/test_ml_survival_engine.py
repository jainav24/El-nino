import pytest
import pandas as pd
import numpy as np
from ml.training.kaplan_meier import generate_kaplan_meier
from ml.training.cox_model import train_cox_model, check_proportional_hazards_assumption
from ml.evaluation.metrics import evaluate_model
from ml.prediction.predictor import predict_survival, calculate_hazard, calculate_risk_category

@pytest.fixture
def mock_survival_df():
    # Simple simulated data to test lifelines integration
    # 20 observations
    np.random.seed(42)
    durations = np.random.randint(30, 200, size=20)
    events = np.random.randint(0, 2, size=20)
    # create covariates
    temp_anomaly = np.random.normal(0, 1, size=20)
    rainfall_anomaly = np.random.normal(0, 1, size=20)
    group = np.random.choice(["A", "B"], size=20)
    
    df = pd.DataFrame({
        "duration": durations,
        "event": events,
        "temp_anomaly": temp_anomaly,
        "rainfall_anomaly": rainfall_anomaly,
        "group": group
    })
    return df

def test_kaplan_meier(mock_survival_df):
    # Overall
    res_all = generate_kaplan_meier(mock_survival_df)
    assert 'All' in res_all
    assert 'survival_probability' in res_all['All']
    
    # Grouped
    res_grouped = generate_kaplan_meier(mock_survival_df, group_col='group')
    assert 'A' in res_grouped
    assert 'B' in res_grouped

def test_cox_model(mock_survival_df):
    # Dummy encoding
    df_encoded = pd.get_dummies(mock_survival_df, columns=['group'], drop_first=True)
    
    cph, results = train_cox_model(df_encoded)
    
    assert cph is not None
    assert 'concordance_index' in results
    assert 'hazard_ratios' in results
    
    # Assumptions
    assumption_res = check_proportional_hazards_assumption(cph, df_encoded)
    assert 'is_reasonable' in assumption_res
    
    # Evaluation
    eval_res = evaluate_model(cph, df_encoded)
    assert 'concordance_index' in eval_res
    
    # Prediction
    # Take first row
    x_test = df_encoded.drop(columns=['duration', 'event']).iloc[[0]]
    times = [30, 60, 90, 120, 180]
    surv_probs = predict_survival(cph, x_test, times)
    assert '30_days' in surv_probs
    assert '180_days' in surv_probs
    
    # Hazard
    haz = calculate_hazard(cph, x_test)
    assert isinstance(haz, float)
    
    # Risk category
    risk = calculate_risk_category(haz)
    assert risk in ["Low", "Medium", "High", "Critical"]
