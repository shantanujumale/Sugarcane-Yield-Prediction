"""
Agronomic Feature Engineering and Lifecycle Stage Definition Module
Directly implements features specified in 'Feature Engineering and feature selection.docx'.
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = 'Yield_Quintal_per_Acre'

def create_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate the 16 scientifically grounded agricultural features defined in research documents.
    """
    df = df.copy()

    # 1. Temperature Range
    if 'Temp_Max_C' in df.columns and 'Temp_Min_C' in df.columns:
        df['Temperature_Range'] = df['Temp_Max_C'] - df['Temp_Min_C']

    # 2. Climate Stress
    if 'Heat_Stress_Days' in df.columns and 'Frost_Days' in df.columns:
        df['Climate_Stress'] = df['Heat_Stress_Days'].fillna(0) + df['Frost_Days'].fillna(0)

    # 3. Soil Water-Retention Potential
    if 'Soil_Depth_cm' in df.columns and 'Water_Holding_Capacity_%' in df.columns:
        df['Water_Retention_Potential'] = (df['Soil_Depth_cm'] * df['Water_Holding_Capacity_%']) / 100.0

    # 4. Nutrient Balances & Soil Fertility Index
    nutrient_cols = ['Nitrogen_kg_per_acre', 'Phosphorus_kg_per_acre', 'Potassium_kg_per_acre']
    if all(c in df.columns for c in nutrient_cols):
        df['NPK_Total'] = df[nutrient_cols].sum(axis=1)
        df['N_to_P'] = df['Nitrogen_kg_per_acre'] / (df['Phosphorus_kg_per_acre'] + 1e-4)
        df['N_to_K'] = df['Nitrogen_kg_per_acre'] / (df['Potassium_kg_per_acre'] + 1e-4)
        df['P_to_K'] = df['Phosphorus_kg_per_acre'] / (df['Potassium_kg_per_acre'] + 1e-4)

    fertility_elements = ['Nitrogen_kg_per_acre', 'Phosphorus_kg_per_acre', 'Potassium_kg_per_acre', 'Organic_Carbon_%']
    if all(c in df.columns for c in fertility_elements):
        z_scores = []
        for col in fertility_elements:
            m = df[col].mean()
            s = df[col].std() if df[col].std() > 0 else 1.0
            z_scores.append((df[col] - m) / s)
        df['Soil_Fertility_Index'] = sum(z_scores) / len(fertility_elements)

    # 5. Irrigation Intensity
    if 'Irrigation_Frequency_Num' in df.columns and 'Water_Quantity_liters_per_acre' in df.columns:
        df['Irrigation_Intensity'] = df['Irrigation_Frequency_Num'] * df['Water_Quantity_liters_per_acre']

    # 6. Biometric Growth Indices
    if 'Cane_Height_cm' in df.columns and 'Cane_Diameter_cm' in df.columns:
        df['Cane_Growth_Index'] = df['Cane_Height_cm'] * df['Cane_Diameter_cm']

    if 'Internode_Length_cm' in df.columns and 'Cane_Height_cm' in df.columns:
        df['Internode_Height_Ratio'] = df['Internode_Length_cm'] / (df['Cane_Height_cm'] + 1e-4)

    # 7. Standardized Stress Index
    if all(c in df.columns for c in ['Heat_Stress_Days', 'Frost_Days', 'Disease_Severity_Num', 'Pest_Level_Num']):
        h_z = (df['Heat_Stress_Days'] - df['Heat_Stress_Days'].mean()) / (df['Heat_Stress_Days'].std() + 1e-4)
        f_z = (df['Frost_Days'] - df['Frost_Days'].mean()) / (df['Frost_Days'].std() + 1e-4)
        df['Stress_Index'] = h_z + f_z + df['Disease_Severity_Num'] + df['Pest_Level_Num']

    # 8. Cyclic Month Encoding
    if 'Month_Num' in df.columns:
        df['Month_Sin'] = np.sin(2 * np.pi * df['Month_Num'] / 12.0)
        df['Month_Cos'] = np.cos(2 * np.pi * df['Month_Num'] / 12.0)

    # 9. Climate x Crop & Resource Interactions
    if 'Rainfall_Total_mm' in df.columns and 'Temp_Avg_C' in df.columns:
        df['Rainfall_Temperature'] = df['Rainfall_Total_mm'] * df['Temp_Avg_C']
    if 'Temp_Avg_C' in df.columns and 'Soil_Moisture_%' in df.columns:
        df['Temperature_SoilMoisture'] = df['Temp_Avg_C'] * df['Soil_Moisture_%']
    if 'Fertilizer_Quantity' in df.columns and 'Water_Quantity_liters_per_acre' in df.columns:
        df['Fertilizer_Irrigation'] = df['Fertilizer_Quantity'] * df['Water_Quantity_liters_per_acre']

    return df

def get_stage_features(stage: int = 1):
    """
    Returns feature dictionary for the 3 defined prediction stages:
    Stage 1: F1 Early-Stage (Pre-Season / Planning)
    Stage 2: F2 Mid-Season (In-Season Biometrics & Stress)
    Stage 3: F3 Late-Season (Pre-Harvest Stalk Biometrics & Maturity)
    """
    f1_numeric = [
        'Temp_Min_C', 'Temp_Max_C', 'Temp_Avg_C', 'Rainfall_Total_mm', 'Rainfall_Seasonal_mm',
        'Humidity_%', 'Solar_Radiation_MJ_m2_day', 'Sunshine_Hours_Decimal', 'Wind_Speed_kmph',
        'Evapotranspiration_mm_day', 'Dew_Point_C', 'Heat_Stress_Days', 'Frost_Days',
        'Soil_pH', 'EC', 'Organic_Carbon_%', 'Sand_%', 'Silt_%', 'Clay_%', 'Soil_Depth_cm',
        'Water_Holding_Capacity_%', 'Nitrogen_kg_per_acre', 'Phosphorus_kg_per_acre',
        'Potassium_kg_per_acre', 'Zinc_mg_per_kg', 'Iron_mg_per_kg', 'Copper_mg_per_kg',
        'Manganese_mg_per_kg', 'Sulfur_kg_per_acre', 'Water_Quantity_liters_per_acre',
        'Groundwater_Level_meters', 'Seed_Rate', 'Row_Spacing_cm', 'Row_Gap_cm', 'Plant_Density',
        'Fertilizer_Quantity', 'Year',
        # Engineered early features
        'Temperature_Range', 'Climate_Stress', 'Water_Retention_Potential',
        'NPK_Total', 'N_to_P', 'N_to_K', 'P_to_K', 'Soil_Fertility_Index',
        'Irrigation_Intensity', 'Month_Sin', 'Month_Cos',
        'Rainfall_Temperature', 'Fertilizer_Irrigation'
    ]

    f1_categorical = [
        'Soil_Type', 'Irrigation_Frequency_Level', 'Irrigation_Method_Type',
        'Water_Quality_Category', 'Intercropping', 'Weed_Control',
        'Soil_Condition_At_Planting', 'Planting_Method', 'Mulching',
        'Fertilizer_Split', 'Drainage_Condition', 'Variety',
        'Fertilizer_Type', 'Application_Timing', 'Machinery_Use',
        'District', 'Season'
    ]

    if stage == 1:
        return {'numeric': f1_numeric, 'categorical': f1_categorical}

    # Stage 2 Additions
    f2_numeric = f1_numeric + [
        'Germination_%', 'Tillering_Count', 'Soil_Moisture_%', 'Pesticide_Usage',
        'Temperature_SoilMoisture', 'Stress_Index'
    ]
    f2_categorical = f1_categorical + [
        'Disease_Type', 'Disease_Severity', 'Pest_Level', 'Growth_Stage'
    ]

    if stage == 2:
        return {'numeric': f2_numeric, 'categorical': f2_categorical}

    # Stage 3 Additions
    f3_numeric = f2_numeric + [
        'Cane_Height_cm', 'Cane_Diameter_cm', 'Internode_Length_cm',
        'Brix_Value', 'Crop_Duration_Days',
        'Cane_Growth_Index', 'Internode_Height_Ratio'
    ]
    f3_categorical = f2_categorical

    return {'numeric': f3_numeric, 'categorical': f3_categorical}

def create_preprocessor(numeric_features, categorical_features, scale_numeric: bool = True):
    """
    Build scikit-learn ColumnTransformer for imputing and encoding.
    """
    if scale_numeric:
        num_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
    else:
        num_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median'))
        ])

    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    return ColumnTransformer([
        ('num', num_pipeline, numeric_features),
        ('cat', cat_pipeline, categorical_features)
    ])
