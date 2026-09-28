import pandas as pd
import numpy as np

def clean_dates(df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
    """Convert specified columns to datetime, dropping invalid formats."""
    df_clean = df.copy()
    for col in date_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    return df_clean

def handle_missing_values(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """
    Handle missing values based on strategy.
    strategy format: {'column_name': 'mean' | 'median' | 'mode' | 'ffill' | 'drop' | constant_value}
    """
    df_clean = df.copy()
    for col, stat in strategy.items():
        if col not in df_clean.columns:
            continue
        if stat == 'mean':
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
        elif stat == 'median':
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
        elif stat == 'mode':
            df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])
        elif stat == 'ffill':
            df_clean[col] = df_clean[col].ffill()
        elif stat == 'drop':
            df_clean = df_clean.dropna(subset=[col])
        else:
            df_clean[col] = df_clean[col].fillna(stat)
    return df_clean

def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
    """Remove exact duplicates or duplicates based on a subset of columns."""
    return df.drop_duplicates(subset=subset, keep='last')

def normalize_categorical(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Strip whitespace and title-case strings to normalize inconsistencies."""
    df_clean = df.copy()
    for col in columns:
        if col in df_clean.columns and df_clean[col].dtype == 'object':
            df_clean[col] = df_clean[col].str.strip().str.title()
    return df_clean

def validate_numerical(df: pd.DataFrame, constraints: dict) -> pd.DataFrame:
    """
    Filter out rows where numerical values fall outside expected bounds.
    constraints format: {'column_name': (min_val, max_val)}
    """
    df_clean = df.copy()
    for col, (min_val, max_val) in constraints.items():
        if col in df_clean.columns:
            # We use boolean masking to keep valid rows or NaNs
            mask = (df_clean[col] >= min_val) & (df_clean[col] <= max_val) | df_clean[col].isna()
            df_clean = df_clean[mask]
    return df_clean

def preprocess_pipeline(df: pd.DataFrame, date_cols=None, fill_strategy=None, cat_cols=None, num_constraints=None) -> pd.DataFrame:
    """Full preprocessing pipeline for a generic dataframe."""
    df = remove_duplicates(df)
    if date_cols:
        df = clean_dates(df, date_cols)
    if fill_strategy:
        df = handle_missing_values(df, fill_strategy)
    if cat_cols:
        df = normalize_categorical(df, cat_cols)
    if num_constraints:
        df = validate_numerical(df, num_constraints)
    return df
