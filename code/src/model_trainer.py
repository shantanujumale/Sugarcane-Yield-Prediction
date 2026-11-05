"""
Model Training, Cross-Validation, Tuning, and Benchmarking Module
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, KFold, cross_validate, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_selection import mutual_info_regression
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from data_loader import load_clean_data
from feature_engineering import (
    create_engineered_features,
    get_stage_features,
    create_preprocessor,
    TARGET_COLUMN
)

RANDOM_STATE = 42

def train_and_benchmark(output_dir: str = None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(output_dir, exist_ok=True)
    root_dir = os.path.join(os.path.dirname(__file__), '..', '..')

    print(">>> Loading clean dataset...", flush=True)
    df_raw = load_clean_data()
    df_eng = create_engineered_features(df_raw)

    # 1. Evaluate and Compare 3 Lifecycle Stages using 5-Fold Cross Validation
    print("\n>>> Comparing 3 Lifecycle Stages (F1 Early vs F2 Mid vs F3 Late)...", flush=True)
    stage_summaries = []
    kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    for stg in [1, 2, 3]:
        spec = get_stage_features(stg)
        X_stg = df_eng[spec['numeric'] + spec['categorical']]
        y_stg = df_eng[TARGET_COLUMN]

        X_tr, X_te, y_tr, y_te = train_test_split(X_stg, y_stg, test_size=0.20, random_state=RANDOM_STATE)
        stg_preproc = create_preprocessor(spec['numeric'], spec['categorical'])
        
        stg_rf = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=RANDOM_STATE, n_jobs=2)
        pipe = Pipeline([('preprocessor', stg_preproc), ('model', stg_rf)])

        cv_res = cross_validate(pipe, X_tr, y_tr, cv=kf, scoring={'mae': 'neg_mean_absolute_error', 'r2': 'r2'}, n_jobs=1)
        stage_summaries.append({
            'Stage': {1: 'F1: Early-Stage (Pre-Season)', 2: 'F2: Mid-Season (Tillering)', 3: 'F3: Late-Season (Maturity)'}[stg],
            'Features_Count': len(spec['numeric']) + len(spec['categorical']),
            'CV_MAE (Q/Acre)': round(-cv_res['test_mae'].mean(), 2),
            'CV_R2': round(cv_res['test_r2'].mean(), 4)
        })

    stage_comparison_df = pd.DataFrame(stage_summaries)
    print(stage_comparison_df.to_string(index=False), flush=True)

    # 2. Comprehensive Modeling using full feature space
    late_spec = get_stage_features(3)
    X = df_eng[late_spec['numeric'] + late_spec['categorical']]
    y = df_eng[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=RANDOM_STATE)

    # Baseline 4 models comparison with 5-fold CV
    models = {
        'Linear (Ridge) Regression': Ridge(alpha=10.0),
        'Decision Tree Regressor': DecisionTreeRegressor(max_depth=10, random_state=RANDOM_STATE),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=15, random_state=RANDOM_STATE, n_jobs=2),
        'XGBoost Regressor': XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=RANDOM_STATE, n_jobs=2)
    }

    cv_benchmark = []
    for name, model in models.items():
        pipe = Pipeline([
            ('preprocessor', create_preprocessor(late_spec['numeric'], late_spec['categorical'])),
            ('model', model)
        ])
        cv_scores = cross_validate(
            pipe, X_train, y_train, cv=kf,
            scoring={'mae': 'neg_mean_absolute_error', 'rmse': 'neg_root_mean_squared_error', 'r2': 'r2'},
            n_jobs=1
        )
        cv_benchmark.append({
            'Model': name,
            'CV_MAE': -cv_scores['test_mae'].mean(),
            'CV_RMSE': -cv_scores['test_rmse'].mean(),
            'CV_R2': cv_scores['test_r2'].mean()
        })
    cv_df = pd.DataFrame(cv_benchmark)
    cv_df.to_csv(os.path.join(output_dir, 'cross_validation_results.csv'), index=False)
    cv_df.to_csv(os.path.join(root_dir, 'cross_validation_results.csv'), index=False)
    print("\n5-Fold Cross-Validation Benchmark on Training Data:\n", cv_df.to_string(index=False), flush=True)

    # 3. Feature Selection
    print("\n>>> Feature Selection via Permutation Importance & Mutual Information...", flush=True)
    full_preproc = create_preprocessor(late_spec['numeric'], late_spec['categorical'])
    full_preproc.fit(X_train)
    X_train_trans = full_preproc.transform(X_train)

    rf_probe = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=RANDOM_STATE, n_jobs=2)
    rf_probe.fit(X_train_trans, y_train)

    perm = permutation_importance(rf_probe, X_train_trans[:200], y_train.iloc[:200], n_repeats=3, random_state=RANDOM_STATE, n_jobs=1)
    perm_df = pd.DataFrame({
        'Feature': full_preproc.get_feature_names_out(),
        'Permutation_Importance': perm.importances_mean
    }).sort_values(by='Permutation_Importance', ascending=False)
    perm_df.to_csv(os.path.join(output_dir, 'permutation_importance.csv'), index=False)
    perm_df.to_csv(os.path.join(root_dir, 'permutation_importance.csv'), index=False)

    num_imp = SimpleImputer(strategy='median').fit_transform(X_train[late_spec['numeric']])
    mi_scores = mutual_info_regression(num_imp, y_train, random_state=RANDOM_STATE)
    mi_df = pd.DataFrame({'Feature': late_spec['numeric'], 'MI_Score': mi_scores}).sort_values(by='MI_Score', ascending=False)

    selected_numeric = mi_df.head(28)['Feature'].tolist()
    for r in ['Water_Quantity_liters_per_acre', 'Nitrogen_kg_per_acre', 'Phosphorus_kg_per_acre', 'Potassium_kg_per_acre', 'Fertilizer_Quantity']:
        if r not in selected_numeric:
            selected_numeric.append(r)

    selected_categorical = [
        'District', 'Season', 'Soil_Type', 'Irrigation_Method_Type', 'Irrigation_Frequency_Level',
        'Fertilizer_Type', 'Variety', 'Disease_Type', 'Disease_Severity', 'Pest_Level', 'Soil_Condition_At_Planting'
    ]
    pd.DataFrame({'Selected_Features': selected_numeric + selected_categorical}).to_csv(os.path.join(root_dir, 'selected_features.csv'), index=False)

    selected_preprocessor = create_preprocessor(selected_numeric, selected_categorical)

    # 4. Hyperparameter Tuning
    print("\n>>> Hyperparameter Tuning on Training Data (RandomizedSearchCV)...", flush=True)
    X_tr_sel = X_train[selected_numeric + selected_categorical]
    X_te_sel = X_test[selected_numeric + selected_categorical]

    rf_dist = {'model__n_estimators': [100, 150], 'model__max_depth': [12, 16], 'model__min_samples_split': [2, 5]}
    rf_tune = RandomizedSearchCV(
        Pipeline([('preprocessor', selected_preprocessor), ('model', RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=2))]),
        rf_dist, n_iter=3, cv=3, scoring='r2', random_state=RANDOM_STATE, n_jobs=1
    )
    rf_tune.fit(X_tr_sel, y_train)
    best_rf = rf_tune.best_estimator_

    xgb_dist = {'model__n_estimators': [100, 150], 'model__max_depth': [4, 6], 'model__learning_rate': [0.06, 0.10]}
    xgb_tune = RandomizedSearchCV(
        Pipeline([('preprocessor', selected_preprocessor), ('model', XGBRegressor(random_state=RANDOM_STATE, n_jobs=2))]),
        xgb_dist, n_iter=3, cv=3, scoring='r2', random_state=RANDOM_STATE, n_jobs=1
    )
    xgb_tune.fit(X_tr_sel, y_train)
    best_xgb = xgb_tune.best_estimator_

    ridge_final = Pipeline([('preprocessor', selected_preprocessor), ('model', Ridge(alpha=10.0))]).fit(X_tr_sel, y_train)
    dt_final = Pipeline([('preprocessor', selected_preprocessor), ('model', DecisionTreeRegressor(max_depth=12, random_state=RANDOM_STATE))]).fit(X_tr_sel, y_train)

    # 5. Final Evaluation on 20% Untouched Test Set
    print("\n>>> Final Evaluation on Untouched 20% Test Set...", flush=True)
    test_evals = []
    pipelines = {
        'Linear (Ridge) Regression': ridge_final,
        'Decision Tree Regressor': dt_final,
        'Tuned Random Forest': best_rf,
        'Tuned XGBoost': best_xgb
    }
    preds_dict = {}

    for name, p in pipelines.items():
        preds = p.predict(X_te_sel)
        preds_dict[name] = preds
        test_evals.append({
            'Model': name,
            'Test_MAE': mean_absolute_error(y_test, preds),
            'Test_RMSE': np.sqrt(mean_squared_error(y_test, preds)),
            'Test_R2': r2_score(y_test, preds)
        })

    eval_df = pd.DataFrame(test_evals).sort_values(by='Test_R2', ascending=False).reset_index(drop=True)
    eval_df.to_csv(os.path.join(output_dir, 'model_comparison.csv'), index=False)
    eval_df.to_csv(os.path.join(root_dir, 'model_comparison.csv'), index=False)
    print(eval_df.to_string(index=False), flush=True)

    champion_name = eval_df.iloc[0]['Model']
    champion_pipeline = pipelines[champion_name]

    # Save champion model
    joblib.dump(champion_pipeline, os.path.join(output_dir, 'sugarcane_yield_best_model.pkl'))
    joblib.dump(champion_pipeline, os.path.join(root_dir, 'sugarcane_yield_best_model.pkl'))

    # Save test sample dataset for SHAP and optimizer
    joblib.dump({
        'X_train_sel': X_tr_sel,
        'X_test_sel': X_te_sel,
        'y_train': y_train,
        'y_test': y_test,
        'best_rf': best_rf,
        'champion_pipeline': champion_pipeline,
        'selected_numeric': selected_numeric,
        'selected_categorical': selected_categorical
    }, os.path.join(output_dir, 'model_data_bundle.joblib'))

    print(f"\nChampion Model: {champion_name} (Test R2: {eval_df.iloc[0]['Test_R2']:.4f}) successfully saved.")
    return champion_pipeline, eval_df, cv_df

if __name__ == '__main__':
    train_and_benchmark()
