import pandas as pd
import numpy as np

def build_survival_dataset(df_policies: pd.DataFrame, df_claims: pd.DataFrame, df_weather: pd.DataFrame, df_enso: pd.DataFrame) -> pd.DataFrame:
    """
    Builds the final survival dataset.
    Strictly avoids data leakage: Features are aggregated ONLY from policy_start_date 
    up to the event/censoring date.
    
    event = 1 when claim occurs
    event = 0 when observation is right-censored (no claim).
    duration = time from policy start to claim event or censoring date.
    """
    
    # 1. Merge claims with policies to determine event and duration
    # Left join ensures we keep all policies (censored ones will have NaN claim details)
    df_merged = pd.merge(df_policies, df_claims, on='policy_id', how='left')
    
    # event: 1 if claim_date is not null, 0 otherwise
    df_merged['event'] = df_merged['claim_date'].notna().astype(int)
    
    # Calculate duration
    # If event == 1, duration = claim_date - policy_start_date
    # If event == 0, duration = policy_end_date - policy_start_date
    end_date = np.where(df_merged['event'] == 1, df_merged['claim_date'], df_merged['policy_end_date'])
    df_merged['end_date_for_calc'] = pd.to_datetime(end_date)
    df_merged['start_date_for_calc'] = pd.to_datetime(df_merged['policy_start_date'])
    
    df_merged['duration'] = (df_merged['end_date_for_calc'] - df_merged['start_date_for_calc']).dt.days
    
    # Basic validation: Drop negative durations (data error)
    df_merged = df_merged[df_merged['duration'] > 0].copy()
    
    # 2. Join Weather and ENSO data without leakage
    # We must aggregate weather data strictly between start_date and end_date_for_calc
    
    # Pre-sort weather and enso for faster merging/querying
    df_weather['date'] = pd.to_datetime(df_weather['date'])
    df_enso['date'] = pd.to_datetime(df_enso['date'])
    
    # Initialize new columns to hold aggregated features
    aggregated_features = []
    
    # Iterate through policies to extract time-window specific features
    # Note: In production with millions of rows, use duckdb or dask for window joins.
    # For this implementation, we will use a groupby/apply approach or iterate.
    for _, row in df_merged.iterrows():
        region = row['region']
        start_d = row['start_date_for_calc']
        end_d = row['end_date_for_calc']
        
        # Filter weather
        w_mask = (df_weather['region'] == region) & (df_weather['date'] >= start_d) & (df_weather['date'] <= end_d)
        w_subset = df_weather[w_mask]
        
        # Filter ENSO (ENSO is often monthly, so we match year/month)
        e_mask = (df_enso['date'] >= start_d.replace(day=1)) & (df_enso['date'] <= end_d)
        e_subset = df_enso[e_mask]
        
        agg = {}
        if not w_subset.empty:
            agg['avg_rainfall_window'] = w_subset['rainfall'].mean()
            agg['avg_temp_window'] = w_subset['temperature'].mean()
            agg['cumulative_rainfall_window'] = w_subset['rainfall'].sum()
            if 'drought_indicator' in w_subset.columns:
                agg['drought_days'] = w_subset['drought_indicator'].sum()
            else:
                agg['drought_days'] = 0
                
            if 'rainfall_anomaly' in w_subset.columns:
                agg['avg_rainfall_anomaly'] = w_subset['rainfall_anomaly'].mean()
            else:
                agg['avg_rainfall_anomaly'] = 0
        else:
            agg['avg_rainfall_window'] = np.nan
            agg['avg_temp_window'] = np.nan
            agg['cumulative_rainfall_window'] = 0
            agg['drought_days'] = 0
            agg['avg_rainfall_anomaly'] = 0
            
        if not e_subset.empty:
            agg['avg_oni_value'] = e_subset['oni_value'].mean()
            # Most frequent phase during the policy period
            agg['primary_enso_phase'] = e_subset['enso_phase'].mode()[0] if not e_subset['enso_phase'].mode().empty else 'Neutral'
        else:
            agg['avg_oni_value'] = np.nan
            agg['primary_enso_phase'] = 'Neutral' # Default if missing
            
        aggregated_features.append(agg)
        
    df_agg = pd.DataFrame(aggregated_features, index=df_merged.index)
    df_final = pd.concat([df_merged, df_agg], axis=1)
    
    # Clean up temp columns
    df_final.drop(columns=['start_date_for_calc', 'end_date_for_calc'], inplace=True, errors='ignore')
    
    # Drop leakage columns (anything that happens after the event)
    leakage_cols = ['claim_amount', 'claim_status', 'claim_reason', 'claim_date', 'claim_id']
    df_final.drop(columns=leakage_cols, inplace=True, errors='ignore')
    
    return df_final
