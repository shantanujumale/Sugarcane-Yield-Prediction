"""
Data Loader and Standardization Module
Loads Maharashtra sugarcane records, converts temporal and sunshine strings,
and encodes ordinal levels for domain calculations.
"""

import os
import numpy as np
import pandas as pd

MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}

ORDINAL_LEVELS = {
    'low': 1.0,
    'medium': 2.0,
    'high': 3.0
}

def parse_sunshine_hours(val):
    """Convert 'HH:MM' string to decimal hours float."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if ':' in val_str:
        try:
            parts = val_str.split(':')
            return float(parts[0]) + float(parts[1]) / 60.0
        except (ValueError, IndexError):
            return np.nan
    try:
        return float(val_str)
    except ValueError:
        return np.nan

def parse_month_to_num(val):
    """Convert month representation (string/abbreviation or integer) to 1-12."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip().lower()
    for abbr, num in MONTH_MAP.items():
        if val_str.startswith(abbr):
            return num
    try:
        num = int(float(val_str))
        if 1 <= num <= 12:
            return num
    except ValueError:
        pass
    return np.nan

def load_clean_data(file_path: str = None) -> pd.DataFrame:
    """
    Load dataset from candidate paths, remove duplicates, and standardize attributes.
    """
    if file_path is None:
        candidates = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'Datasets', 'FINAL_SUGARCANE_DATASET.csv'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'Datasets', 'FINAL_SUGARCANE_DATASET(2).csv'),
            os.path.join('Datasets', 'FINAL_SUGARCANE_DATASET.csv'),
            os.path.join('Datasets', 'FINAL_SUGARCANE_DATASET(2).csv'),
            os.path.join('Code', 'FINAL_SUGARCANE_DATASET.csv'),
            'FINAL_SUGARCANE_DATASET.csv',
            'FINAL_SUGARCANE_DATASET(2).csv'
        ]
        for p in candidates:
            if os.path.exists(p):
                file_path = p
                break

    if file_path is None or not os.path.exists(file_path):
        raise FileNotFoundError(f"Sugarcane dataset not found at {file_path}")

    df = pd.read_csv(file_path)
    df = df.drop_duplicates().reset_index(drop=True)

    # Convert Sunshine_Hours_hh_mm to decimal
    if 'Sunshine_Hours_hh_mm' in df.columns:
        df['Sunshine_Hours_Decimal'] = df['Sunshine_Hours_hh_mm'].apply(parse_sunshine_hours)
        df = df.drop(columns=['Sunshine_Hours_hh_mm'])

    # Standardize Month column
    if 'Month' in df.columns:
        df['Month_Num'] = df['Month'].apply(parse_month_to_num).fillna(6).astype(int)

    # Ordinal numeric mappings for physical index creation
    if 'Irrigation_Frequency_Level' in df.columns:
        df['Irrigation_Frequency_Num'] = df['Irrigation_Frequency_Level'].astype(str).str.lower().map(ORDINAL_LEVELS).fillna(2.0)
    if 'Disease_Severity' in df.columns:
        df['Disease_Severity_Num'] = df['Disease_Severity'].astype(str).str.lower().map(ORDINAL_LEVELS).fillna(1.0)
    if 'Pest_Level' in df.columns:
        df['Pest_Level_Num'] = df['Pest_Level'].astype(str).str.lower().map(ORDINAL_LEVELS).fillna(1.0)
    if 'Water_Quality_Category' in df.columns:
        df['Water_Quality_Num'] = df['Water_Quality_Category'].astype(str).str.lower().map({'saline': 1.0, 'moderate': 2.0, 'good': 3.0}).fillna(2.0)

    return df

if __name__ == '__main__':
    df = load_clean_data()
    print(f"Data loaded successfully! Shape: {df.shape}")
    print(f"Sunshine Hours Summary:\n{df['Sunshine_Hours_Decimal'].describe()}")
