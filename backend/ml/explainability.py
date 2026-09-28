import numpy as np
import pandas as pd

# Mapping of encoded features to human-readable names for explanation
FEATURE_NAME_MAP = {
    'derived_rainfall_deviation': 'Rainfall Deficit',
    'precipitation_anomaly_pct': 'Precipitation Anomaly',
    'derived_temperature_anomaly': 'High Temperature Anomaly',
    'drought_severity': 'High Drought Severity',
    'flood_severity': 'Flood Severity',
    'humidity_anomaly': 'Humidity Anomaly',
    'extreme_temperature_indicator': 'Extreme Temperature',
    'extreme_rainfall_indicator': 'Extreme Rainfall',
    'consecutive_dry_days_proxy': 'Consecutive Dry Days',
    'el_nino_indicator': 'El Niño Conditions',
    'el_nino_intensity_numeric': 'El Niño Intensity',
    'derived_enso_category_Strong El Niño': 'Strong El Niño Conditions',
    'duration_of_episode_months': 'El Niño Duration',
    'elnino_x_rainfall_dev': 'El Niño exacerbated Rainfall Deficit',
    'elnino_x_drought_index': 'El Niño exacerbated Drought Severity',
    'elnino_x_temperature_anomaly': 'El Niño exacerbated Temperature Anomaly',
    'elnino_x_soil_moisture': 'El Niño impacted Soil Moisture',
    'crop_x_rainfall_dev': 'Crop Vulnerability to Rainfall',
    'crop_x_drought': 'Crop Vulnerability to Drought',
    'irrigation_x_drought': 'Irrigation Vulnerability to Drought',
    'region_x_elnino': 'Regional El Niño Impact',
    'soil_moisture': 'Low Soil Moisture',
    'farm_area': 'Farm Area',
    'historical_claim_rate': 'Previous Claim History',
    'irrigation_type_Rainfed': 'Poor Irrigation (Rainfed)'
}

def get_readable_name(feature):
    if feature in FEATURE_NAME_MAP:
        return FEATURE_NAME_MAP[feature]
    # Clean up dummy names like 'crop_type_Rice'
    if '_' in feature:
        parts = feature.split('_')
        return " ".join([p.capitalize() for p in parts])
    return feature.capitalize()

def explain_prediction(model, input_data_scaled_df):
    """
    Computes the partial hazard components for the input data based on Cox model coefficients.
    Returns the log-hazard contributions for each feature.
    """
    contributions = {}
    
    # model.params_ contains the log hazard ratios (coefficients)
    for col in input_data_scaled_df.columns:
        if col in model.params_.index:
            coef = model.params_[col]
            val = input_data_scaled_df[col].iloc[0]
            # Contribution to log partial hazard
            contribution = coef * val
            contributions[col] = contribution
            
    return contributions

def get_top_risk_factors(contributions, top_n=3):
    """
    Identify features increasing the hazard (positive contribution).
    """
    # Sort descending
    sorted_cont = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    # Filter for positive
    risk_factors = [(k, v) for k, v in sorted_cont if v > 0]
    return risk_factors[:top_n]

def get_protective_factors(contributions, top_n=3):
    """
    Identify features decreasing the hazard (negative contribution).
    """
    # Sort ascending
    sorted_cont = sorted(contributions.items(), key=lambda x: x[1])
    # Filter for negative
    protective = [(k, v) for k, v in sorted_cont if v < 0]
    return protective[:top_n]

def generate_risk_summary(risk_category, top_risk_factors, top_protective_factors):
    """
    Generates a human-readable explanation of the risk.
    """
    summary = f"{risk_category} Risk: "
    
    if risk_category == "High":
        summary += "The policy shows elevated agricultural claim risk primarily because of "
    elif risk_category == "Medium":
        summary += "The policy shows moderate agricultural claim risk influenced by "
    else:
        summary += "The policy shows low agricultural claim risk. The risk is minimized by "
        
    risk_names = [get_readable_name(f[0]).lower() for f in top_risk_factors]
    
    if risk_category in ["High", "Medium"] and risk_names:
        if len(risk_names) > 1:
            summary += ", ".join(risk_names[:-1]) + f", and {risk_names[-1]}."
        else:
            summary += f"{risk_names[0]}."
            
        # Mention protective factors if any
        prot_names = [get_readable_name(f[0]).lower() for f in top_protective_factors]
        if prot_names:
            summary += f" However, this is partially offset by {prot_names[0]}."
    else:
        prot_names = [get_readable_name(f[0]).lower() for f in top_protective_factors]
        if len(prot_names) > 1:
            summary += ", ".join(prot_names[:-1]) + f", and {prot_names[-1]}."
        elif prot_names:
            summary += f"{prot_names[0]}."
        else:
            summary += "overall favorable conditions."
            
    return summary
