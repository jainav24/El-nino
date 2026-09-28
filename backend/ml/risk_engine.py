# -*- coding: utf-8 -*-
"""
Risk Assessment Engine
======================
Combines input validation, feature engineering, survival model prediction,
and explainability into a single JSON-ready pipeline.

Usage:
    engine = RiskEngine()
    result = engine.predict(scenario_dict)
    comparison = engine.what_if_analysis(current_scenario, alternative_scenario)
"""

import numpy as np
import pandas as pd
import pickle
import os
# LabelEncoder replaced by CATEGORICAL_ORDINALS dict for deterministic inference

from backend.ml.explainability import (
    explain_prediction,
    get_top_risk_factors,
    get_protective_factors,
    generate_risk_summary,
    get_readable_name,
)

# ──────────────────────────────────────────────
# Paths – resolved relative to project root
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PIPELINE_DIR = os.path.join(BASE_DIR, "data", "processed", "ml_pipeline_output")
MODEL_DIR = os.path.join(BASE_DIR, "data", "processed", "model_output")

# ──────────────────────────────────────────────
# Valid values for categorical inputs
# ──────────────────────────────────────────────
VALID_STATES = ['Andhra Pradesh', 'Karnataka', 'Madhya Pradesh',
                'Maharashtra', 'Punjab', 'Uttar Pradesh']
VALID_CROP_TYPES = ['Cotton', 'Maize', 'Rice', 'Soybean', 'Sugarcane', 'Wheat']
VALID_CROP_SEASONS = ['Kharif', 'Rabi', 'Zaid']
VALID_SOIL_TYPES = ['Alluvial', 'Black', 'Laterite', 'Loamy', 'Red']
VALID_IRRIGATION_TYPES = ['Canal', 'Drip', 'Rainfed', 'Tube Well']
VALID_ELNINO_STATUSES = ['Active El Nino', 'La Nina', 'Neutral']
VALID_ELNINO_INTENSITIES = ['La Nina', 'Moderate El Nino',
                            'Strong El Nino', 'Weak El Nino']

# ──────────────────────────────────────────────
# Numeric input constraints  (min, max, description)
# ──────────────────────────────────────────────
NUMERIC_BOUNDS = {
    'latitude':              (6.0,   38.0,   'Latitude (India)'),
    'longitude':             (68.0,  98.0,   'Longitude (India)'),
    'farm_area':             (0.1,   500.0,  'Farm area (hectares)'),
    'enso_index':            (-3.0,  3.0,    'ENSO / ONI index'),
    'normal_rainfall':       (0.0,   5000.0, 'Normal rainfall (mm)'),
    'rainfall':              (0.0,   8000.0, 'Observed rainfall (mm)'),
    'rainfall_deviation':    (-5000, 5000,   'Rainfall deviation (mm)'),
    'temperature':           (-10.0, 55.0,   'Temperature (°C)'),
    'temperature_deviation': (-15.0, 15.0,   'Temperature deviation (°C)'),
    'humidity':              (0.0,   100.0,  'Humidity (%)'),
    'soil_moisture':         (0.0,   1.0,    'Soil moisture (0–1)'),
    'drought_index':         (0.0,   1.0,    'Drought index (0–1)'),
    'flood_index':           (0.0,   1.0,    'Flood index (0–1)'),
    'extreme_weather_events':(0,     50,     'Extreme weather event count'),
    'weather_anomaly_score': (0.0,   1.0,    'Weather anomaly score (0–1)'),
    'historical_yield':      (0.0,   20000,  'Historical yield (kg/ha)'),
    'insurance_amount':      (0.0,   1e8,    'Insurance amount (INR)'),
    'premium_amount':        (0.0,   1e7,    'Premium amount (INR)'),
    'previous_claims':       (0,     100,    'Previous claim count'),
}

# ──────────────────────────────────────────────
# Fixed categorical ordinal mappings (must match training-time LabelEncoder order)
# Sorted alphabetically — the default behaviour of sklearn LabelEncoder
# ──────────────────────────────────────────────
CATEGORICAL_ORDINALS = {
    'crop_type':       {v: i for i, v in enumerate(sorted(VALID_CROP_TYPES))},
    'state':           {v: i for i, v in enumerate(sorted(VALID_STATES))},
    'irrigation_type': {v: i for i, v in enumerate(sorted(VALID_IRRIGATION_TYPES))},
}

# ──────────────────────────────────────────────
# Thresholds for risk categories
# ──────────────────────────────────────────────
# Based on claim probability within 180 days
HIGH_RISK_THRESHOLD = 0.50   # ≥ 50 % claim probability → High
MEDIUM_RISK_THRESHOLD = 0.25 # ≥ 25 % → Medium

# Time-points of interest (days)
EVALUATION_TIMES = [30, 90, 180, 365]


# ═══════════════════════════════════════════════
# Input Validation
# ═══════════════════════════════════════════════
class ValidationError(Exception):
    """Raised when input data fails validation."""
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__(f"Validation failed with {len(errors)} error(s).")


def validate_input(data: dict) -> list:
    """
    Validates a raw scenario dictionary.
    Returns a list of human-readable error strings.  Empty means valid.
    """
    errors = []

    # ── Required fields ──
    required_categorical = {
        'state':            VALID_STATES,
        'crop_type':        VALID_CROP_TYPES,
        'crop_season':      VALID_CROP_SEASONS,
        'soil_type':        VALID_SOIL_TYPES,
        'irrigation_type':  VALID_IRRIGATION_TYPES,
        'elnino_status':    VALID_ELNINO_STATUSES,
        'elnino_intensity': VALID_ELNINO_INTENSITIES,
    }

    for field, valid_vals in required_categorical.items():
        if field not in data:
            errors.append(f"Missing required field: '{field}'.")
        elif data[field] not in valid_vals:
            errors.append(
                f"Invalid value '{data[field]}' for '{field}'. "
                f"Must be one of: {valid_vals}."
            )

    # ── Numeric bounds ──
    for field, (lo, hi, label) in NUMERIC_BOUNDS.items():
        if field not in data:
            errors.append(f"Missing required numeric field: '{field}' ({label}).")
        else:
            try:
                val = float(data[field])
                if val < lo or val > hi:
                    errors.append(
                        f"'{field}' ({label}) value {val} is out of "
                        f"valid range [{lo}, {hi}]."
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"'{field}' ({label}) must be numeric, got: {data[field]}."
                )

    return errors


# ═══════════════════════════════════════════════
# Feature Engineering  (mirrors feature_engineering.py)
# ═══════════════════════════════════════════════
def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the exact same derived-feature logic used during training.
    Operates on a 1-row DataFrame with raw columns.
    """
    # Module 1 – Weather
    df['derived_rainfall_deviation'] = df['rainfall'] - df['normal_rainfall']
    df['derived_temperature_anomaly'] = df['temperature'] - 28.0
    df['precipitation_anomaly_pct'] = (
        df['derived_rainfall_deviation'] / df['normal_rainfall']
    ) * 100
    df['derived_soil_moisture_anomaly'] = 1.0 - df['soil_moisture']
    df['drought_severity'] = np.clip(
        df['derived_soil_moisture_anomaly'] + df['derived_temperature_anomaly'] * 0.1,
        0, 1.0,
    )
    df['flood_severity'] = np.clip(
        df['derived_rainfall_deviation'] / 800.0, 0, 1.0
    )
    df['humidity_anomaly'] = df['humidity'] - 65.0
    df['extreme_temperature_indicator'] = (
        df['derived_temperature_anomaly'] > 2.5
    ).astype(int)
    df['extreme_rainfall_indicator'] = (
        df['derived_rainfall_deviation'] > 500
    ).astype(int)
    df['consecutive_dry_days_proxy'] = np.round(df['drought_severity'] * 45)
    df['base_weather_anomaly_score'] = (
        df['drought_severity'] * 0.5
        + df['flood_severity'] * 0.3
        + df['extreme_temperature_indicator'] * 0.2
    )

    # Module 2 – El Niño
    conditions = [
        (df['enso_index'] >= 1.5),
        (df['enso_index'] >= 1.0) & (df['enso_index'] < 1.5),
        (df['enso_index'] >= 0.5) & (df['enso_index'] < 1.0),
        (df['enso_index'] > -0.5) & (df['enso_index'] < 0.5),
        (df['enso_index'] <= -0.5),
    ]
    choices = ['Strong El Niño', 'Moderate El Niño',
               'Weak El Niño', 'Neutral', 'La Niña']
    df['derived_enso_category'] = np.select(conditions, choices, default='Neutral')
    df['el_nino_indicator'] = (df['enso_index'] >= 0.5).astype(int)
    df['el_nino_intensity_numeric'] = np.clip(df['enso_index'], 0, None)
    # Deterministic duration: avoids random values at inference time
    df['duration_of_episode_months'] = np.where(
        df['el_nino_indicator'] == 1,
        np.clip((np.abs(df['enso_index']) * 8 + 4).astype(int), 6, 18),
        0,
    )

    # Module 3 – Interactions (use fixed ordinal mappings, NOT fit_transform)
    crop_encoded = df['crop_type'].map(CATEGORICAL_ORDINALS['crop_type']).fillna(0).values
    region_encoded = df['state'].map(CATEGORICAL_ORDINALS['state']).fillna(0).values
    irrigation_encoded = df['irrigation_type'].map(CATEGORICAL_ORDINALS['irrigation_type']).fillna(0).values

    df['elnino_x_rainfall_dev'] = (
        df['el_nino_indicator'].values * df['derived_rainfall_deviation'].values
    )
    df['elnino_x_drought_index'] = (
        df['el_nino_indicator'].values * df['drought_severity'].values
    )
    df['elnino_x_temperature_anomaly'] = (
        df['el_nino_indicator'].values * df['derived_temperature_anomaly'].values
    )
    df['elnino_x_soil_moisture'] = (
        df['el_nino_indicator'].values * df['soil_moisture'].values
    )
    df['crop_x_rainfall_dev'] = (
        crop_encoded * df['derived_rainfall_deviation'].values
    )
    df['crop_x_drought'] = crop_encoded * df['drought_severity'].values
    df['irrigation_x_drought'] = irrigation_encoded * df['drought_severity'].values
    df['region_x_elnino'] = region_encoded * df['el_nino_indicator'].values

    # Module 4 – Preliminary Risk Score
    raw_score = (
        df['drought_severity'] * 40
        + df['flood_severity'] * 30
        + df['extreme_temperature_indicator'] * 15
        + (df['el_nino_intensity_numeric'] / 2.5) * 15
    )
    df['preliminary_weather_risk_score'] = np.clip(
        np.round(raw_score, 0), 0, 100
    ).astype(int)

    return df


# ═══════════════════════════════════════════════
# Risk Engine
# ═══════════════════════════════════════════════
class RiskEngine:
    """
    Orchestrates: input → validation → feature engineering →
    survival model → prediction → explanation → JSON output.
    """

    def __init__(self):
        # Load trained Cox model
        model_path = os.path.join(MODEL_DIR, "cph_proposed_model.pkl")
        with open(model_path, "rb") as f:
            self.cox_model = pickle.load(f)

        # Load scaler, column lists
        with open(os.path.join(PIPELINE_DIR, "scaler.pkl"), "rb") as f:
            self.scaler = pickle.load(f)
        with open(os.path.join(PIPELINE_DIR, "model_columns.pkl"), "rb") as f:
            self.model_columns = pickle.load(f)
        with open(os.path.join(PIPELINE_DIR, "scale_cols.pkl"), "rb") as f:
            self.scale_cols = pickle.load(f)

        # The Cox model was trained without the target columns and
        # without 'preliminary_weather_risk_score'.
        self.cox_feature_cols = [
            c for c in self.model_columns
            if c not in ['time_to_claim', 'claim_occurred',
                         'preliminary_weather_risk_score']
        ]

    # ── public API ────────────────────────────

    def predict(self, scenario: dict) -> dict:
        """
        Full prediction pipeline.  Returns a JSON-serialisable dict.
        """
        # 1. Validate
        errors = validate_input(scenario)
        if errors:
            return {"success": False, "errors": errors}

        # 2. Build single-row DataFrame
        df = self._build_dataframe(scenario)

        # 3. Feature engineering
        df = _engineer_features(df)

        # 4. Encode & scale
        df_model = self._encode_and_scale(df)

        # 5. Predict survival function
        surv_func = self.cox_model.predict_survival_function(df_model)
        # surv_func is a DataFrame indexed by time
        surv_series = surv_func.iloc[:, 0]

        # 6. Extract metrics at key times
        survival_at = {}
        claim_prob_at = {}
        for t in EVALUATION_TIMES:
            idx = surv_series.index[surv_series.index <= t]
            if len(idx) > 0:
                s = float(surv_series.loc[idx[-1]])
            else:
                s = 1.0
            survival_at[f"{t}_days"] = round(s, 4)
            claim_prob_at[f"{t}_days"] = round(1 - s, 4)

        # Median survival time (estimated time-to-claim)
        median_raw = self.cox_model.predict_median(df_model)
        # lifelines may return a scalar or a Series depending on version
        if hasattr(median_raw, 'iloc'):
            median_survival = float(median_raw.iloc[0])
        else:
            median_survival = float(median_raw)
        if np.isinf(median_survival):
            median_survival_str = "> 365 days (low risk)"
            median_survival_val = None
        else:
            median_survival_val = round(float(median_survival), 1)
            median_survival_str = f"{median_survival_val} days"

        # 7. Overall risk score (0-100) and category
        claim_prob_180 = claim_prob_at.get("180_days", 0)
        risk_score = round(claim_prob_180 * 100, 1)

        if claim_prob_180 >= HIGH_RISK_THRESHOLD:
            risk_category = "High"
        elif claim_prob_180 >= MEDIUM_RISK_THRESHOLD:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        # 8. Explainability
        contributions = explain_prediction(self.cox_model, df_model)
        top_risk = get_top_risk_factors(contributions, top_n=5)
        top_protective = get_protective_factors(contributions, top_n=3)
        summary_text = generate_risk_summary(
            risk_category, top_risk, top_protective
        )

        # 9. Build detailed factor breakdown
        risk_factor_details = [
            {
                "feature": f,
                "readable_name": get_readable_name(f),
                "contribution": round(float(v), 4),
                "direction": "increases risk" if v > 0 else "decreases risk",
                "hazard_ratio": round(float(np.exp(self.cox_model.params_[f])), 4)
                    if f in self.cox_model.params_.index else None,
            }
            for f, v in sorted(contributions.items(),
                               key=lambda x: abs(x[1]), reverse=True)[:10]
        ]

        # 10. Assemble response
        return {
            "success": True,
            "overall_risk_score": risk_score,
            "risk_category": risk_category,
            "estimated_time_to_claim": median_survival_str,
            "estimated_time_to_claim_days": median_survival_val,
            "survival_probability": survival_at,
            "claim_probability": claim_prob_at,
            "explanation": summary_text,
            "top_contributing_factors": risk_factor_details,
            "preliminary_weather_risk_score": int(
                df['preliminary_weather_risk_score'].iloc[0]
            ),
        }

    def what_if_analysis(self, current: dict, alternative: dict) -> dict:
        """
        Compares two scenarios and shows how the predicted risk changes.
        """
        result_current = self.predict(current)
        if not result_current.get("success"):
            return {
                "success": False,
                "errors": ["Current scenario validation failed."]
                          + result_current.get("errors", []),
            }

        result_alternative = self.predict(alternative)
        if not result_alternative.get("success"):
            return {
                "success": False,
                "errors": ["Alternative scenario validation failed."]
                          + result_alternative.get("errors", []),
            }

        # Compute deltas
        delta_risk = round(
            result_alternative["overall_risk_score"]
            - result_current["overall_risk_score"], 2
        )
        delta_direction = (
            "decreased" if delta_risk < 0
            else "increased" if delta_risk > 0
            else "unchanged"
        )

        # Changed inputs
        changed_fields = {
            k: {"from": current[k], "to": alternative[k]}
            for k in alternative
            if k in current and current[k] != alternative[k]
        }

        return {
            "success": True,
            "current_scenario": {
                "risk_score": result_current["overall_risk_score"],
                "risk_category": result_current["risk_category"],
                "claim_probability_180d": result_current["claim_probability"].get(
                    "180_days"
                ),
                "explanation": result_current["explanation"],
            },
            "alternative_scenario": {
                "risk_score": result_alternative["overall_risk_score"],
                "risk_category": result_alternative["risk_category"],
                "claim_probability_180d": result_alternative["claim_probability"].get(
                    "180_days"
                ),
                "explanation": result_alternative["explanation"],
            },
            "delta_risk_score": delta_risk,
            "delta_direction": delta_direction,
            "changed_inputs": changed_fields,
            "what_if_summary": (
                f"Changing {', '.join(changed_fields.keys())} "
                f"{delta_direction} the predicted risk by "
                f"{abs(delta_risk):.1f} percentage points "
                f"(from {result_current['risk_category']} to "
                f"{result_alternative['risk_category']})."
            ),
        }

    # ── private helpers ───────────────────────

    def _build_dataframe(self, scenario: dict) -> pd.DataFrame:
        """Converts a flat dict into a single-row DataFrame with raw columns."""
        raw_cols = [
            'state', 'latitude', 'longitude', 'crop_type', 'crop_season',
            'farm_area', 'soil_type', 'irrigation_type', 'elnino_status',
            'enso_index', 'elnino_intensity', 'normal_rainfall', 'rainfall',
            'rainfall_deviation', 'temperature', 'temperature_deviation',
            'humidity', 'soil_moisture', 'drought_index', 'flood_index',
            'extreme_weather_events', 'weather_anomaly_score',
            'historical_yield', 'insurance_amount', 'premium_amount',
            'previous_claims',
        ]
        row = {col: scenario.get(col) for col in raw_cols}
        df = pd.DataFrame([row])

        # Cast numerics
        for col in df.columns:
            if col not in ['state', 'crop_type', 'crop_season',
                           'soil_type', 'irrigation_type',
                           'elnino_status', 'elnino_intensity']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def _encode_and_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        One-hot encodes and scales a single-row DF to match the training
        schema exactly.
        """
        # Drop columns that were dropped during training
        drop_cols = ['policy_id', 'farmer_id', 'district', 'current_yield']
        df = df.drop(columns=[c for c in drop_cols if c in df.columns],
                     errors='ignore')

        # One-hot encode
        categorical = df.select_dtypes(include=['object']).columns.tolist()
        df = pd.get_dummies(df, columns=categorical, drop_first=True)

        # Align columns to training schema
        for col in self.model_columns:
            if col not in df.columns:
                df[col] = 0
        df = df[self.model_columns]

        # Scale the same columns the training pipeline scaled
        cols_to_scale = [c for c in self.scale_cols if c in df.columns]
        df[cols_to_scale] = self.scaler.transform(df[cols_to_scale])

        # Drop target / non-feature columns
        df = df.drop(
            columns=['time_to_claim', 'claim_occurred',
                     'preliminary_weather_risk_score'],
            errors='ignore',
        )

        return df


# ═══════════════════════════════════════════════
# Demo / test
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    engine = RiskEngine()

    # ── Test 1: High-risk scenario ──
    high_risk_scenario = {
        "state": "Maharashtra",
        "latitude": 19.0,
        "longitude": 75.0,
        "crop_type": "Cotton",
        "crop_season": "Kharif",
        "farm_area": 5.0,
        "soil_type": "Black",
        "irrigation_type": "Rainfed",
        "elnino_status": "Active El Nino",
        "enso_index": 2.0,
        "elnino_intensity": "Strong El Nino",
        "normal_rainfall": 800.0,
        "rainfall": 400.0,
        "rainfall_deviation": -400.0,
        "temperature": 35.0,
        "temperature_deviation": 5.0,
        "humidity": 40.0,
        "soil_moisture": 0.15,
        "drought_index": 0.85,
        "flood_index": 0.0,
        "extreme_weather_events": 3,
        "weather_anomaly_score": 0.8,
        "historical_yield": 1200.0,
        "insurance_amount": 150000.0,
        "premium_amount": 5000.0,
        "previous_claims": 2,
    }

    print("=" * 70)
    print("  TEST 1: HIGH-RISK PREDICTION")
    print("=" * 70)
    result = engine.predict(high_risk_scenario)

    if result["success"]:
        print(f"\n  Overall Risk Score : {result['overall_risk_score']}%")
        print(f"  Risk Category      : {result['risk_category']}")
        print(f"  Est. Time-to-Claim : {result['estimated_time_to_claim']}")
        print(f"  Weather Risk Score : {result['preliminary_weather_risk_score']}")
        print(f"\n  Survival Probability:")
        for k, v in result["survival_probability"].items():
            print(f"    {k:>10s} --> {v:.2%}")
        print(f"\n  Claim Probability:")
        for k, v in result["claim_probability"].items():
            print(f"    {k:>10s} --> {v:.2%}")
        print(f"\n  Explanation:\n  {result['explanation']}")
        print(f"\n  Top Contributing Factors:")
        for f in result["top_contributing_factors"]:
            print(f"    * {f['readable_name']:40s} | "
                  f"contribution={f['contribution']:+.4f} | "
                  f"{f['direction']} | HR={f['hazard_ratio']}")
    else:
        print(f"  ERRORS: {result['errors']}")

    # ── Test 2: What-if Analysis ──
    alt_scenario = high_risk_scenario.copy()
    alt_scenario["rainfall"] = 750.0
    alt_scenario["rainfall_deviation"] = -50.0
    alt_scenario["irrigation_type"] = "Drip"
    alt_scenario["soil_moisture"] = 0.55
    alt_scenario["drought_index"] = 0.3
    alt_scenario["enso_index"] = 0.2
    alt_scenario["elnino_intensity"] = "Weak El Nino"
    alt_scenario["elnino_status"] = "Neutral"

    print("\n" + "=" * 70)
    print("  TEST 2: WHAT-IF ANALYSIS")
    print("=" * 70)
    comparison = engine.what_if_analysis(high_risk_scenario, alt_scenario)

    if comparison["success"]:
        c = comparison["current_scenario"]
        a = comparison["alternative_scenario"]
        print(f"\n  Current:     {c['risk_score']}% ({c['risk_category']})")
        print(f"  Alternative: {a['risk_score']}% ({a['risk_category']})")
        print(f"  Delta:       {comparison['delta_risk_score']:+.1f} pp "
              f"({comparison['delta_direction']})")
        print(f"\n  Changed Inputs:")
        for k, v in comparison["changed_inputs"].items():
            print(f"    {k:25s}: {v['from']} --> {v['to']}")
        print(f"\n  Summary: {comparison['what_if_summary']}")
    else:
        print(f"  ERRORS: {comparison['errors']}")

    # ── Test 3: Validation safeguards ──
    print("\n" + "=" * 70)
    print("  TEST 3: VALIDATION SAFEGUARDS")
    print("=" * 70)
    bad_scenario = {
        "state": "InvalidState",
        "rainfall": -100,
        "temperature": 999,
        "farm_area": -5,
        "crop_type": "Mango",
        "enso_index": 10,
    }
    result = engine.predict(bad_scenario)
    if not result["success"]:
        print(f"\n  Caught {len(result['errors'])} validation errors:")
        for e in result["errors"]:
            print(f"    X {e}")
