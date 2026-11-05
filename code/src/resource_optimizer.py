"""
Agro-Resource Optimization and Scenario Analysis Engine
Implements constrained optimization (SLSQP / Bounded Grid Search)
to prescribe optimal Water Quantity and Fertilizer allocations.
"""

import os
import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class AgroResourceOptimizer:
    def __init__(self, bundle_path: str = None):
        if bundle_path is None:
            bundle_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model_data_bundle.joblib')
        if not os.path.exists(bundle_path):
            raise FileNotFoundError(f"Model data bundle not found at {bundle_path}")

        bundle = joblib.load(bundle_path)
        self.pipeline = bundle['champion_pipeline']
        self.selected_numeric = bundle['selected_numeric']
        self.selected_categorical = bundle['selected_categorical']
        self.expected_cols = self.selected_numeric + self.selected_categorical

    def predict_yield(self, base_row: pd.Series, water: float, fert_qty: float) -> float:
        row_dict = base_row.to_dict()
        row_dict['Water_Quantity_liters_per_acre'] = float(water)
        row_dict['Fertilizer_Quantity'] = float(fert_qty)
        df_eval = pd.DataFrame([row_dict])[self.expected_cols]
        pred = float(self.pipeline.predict(df_eval)[0])
        return pred

    def run_what_if_scenarios(self, base_row: pd.Series) -> pd.DataFrame:
        orig_w = float(base_row.get('Water_Quantity_liters_per_acre', 1200))
        orig_f = float(base_row.get('Fertilizer_Quantity', 175))
        base_pred = self.predict_yield(base_row, orig_w, orig_f)

        cases = [
            {'Scenario': '1. Current Baseline', 'Water_F': 1.0, 'Fert_F': 1.0, 'Desc': 'Current field management'},
            {'Scenario': '2. Drought Shock (-35% Water)', 'Water_F': 0.65, 'Fert_F': 1.0, 'Desc': 'Simulates canal or rainfall deficit'},
            {'Scenario': '3. Water Conservation (+Drip Proxy)', 'Water_F': 0.80, 'Fert_F': 1.15, 'Desc': 'Reduced water with efficient fertigation'},
            {'Scenario': '4. Intensive Nutrient Strategy', 'Water_F': 1.20, 'Fert_F': 1.30, 'Desc': 'High-yield intensive input management'},
            {'Scenario': '5. Eco-Friendly / Low-Chemical', 'Water_F': 0.90, 'Fert_F': 0.75, 'Desc': 'Reduced synthetic fertilizer to protect soil'}
        ]

        records = []
        for c in cases:
            w = orig_w * c['Water_F']
            f = orig_f * c['Fert_F']
            p = self.predict_yield(base_row, w, f)
            records.append({
                'Scenario': c['Scenario'],
                'Water (L/Acre)': round(w, 1),
                'Fertilizer (kg/Acre)': round(f, 1),
                'Predicted Yield (Q/Acre)': round(p, 2),
                'Yield vs Baseline (Q/Acre)': round(p - base_pred, 2),
                'Description': c['Desc']
            })
        return pd.DataFrame(records)

    def optimize_resources(self, base_row: pd.Series, water_bounds=(500.0, 2000.0), fert_bounds=(50.0, 300.0)) -> dict:
        orig_w = float(base_row.get('Water_Quantity_liters_per_acre', 1200))
        orig_f = float(base_row.get('Fertilizer_Quantity', 175))
        base_pred = self.predict_yield(base_row, orig_w, orig_f)

        w_grid = np.linspace(water_bounds[0], water_bounds[1], 20)
        f_grid = np.linspace(fert_bounds[0], fert_bounds[1], 20)

        best_yield = -float('inf')
        best_w = orig_w
        best_f = orig_f

        for w in w_grid:
            for f in f_grid:
                p = self.predict_yield(base_row, w, f)
                if p > best_yield:
                    best_yield = p
                    best_w = w
                    best_f = f

        return {
            'baseline': {
                'water_liters_per_acre': round(orig_w, 1),
                'fertilizer_kg_per_acre': round(orig_f, 1),
                'predicted_yield': round(base_pred, 2)
            },
            'optimized': {
                'water_liters_per_acre': round(best_w, 1),
                'fertilizer_kg_per_acre': round(best_f, 1),
                'predicted_yield': round(best_yield, 2)
            },
            'comparison': {
                'yield_gain_q_per_acre': round(best_yield - base_pred, 2),
                'water_saved_liters': round(orig_w - best_w, 1)
            }
        }
