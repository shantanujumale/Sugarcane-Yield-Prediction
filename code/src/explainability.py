"""
Explainable AI (XAI) Module using SHAP TreeExplainer
Generates global feature attribution plots, local waterfall breakdowns,
and agronomic interpretation text.
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt
import plotly.graph_objects as go

class SugarcaneExplainer:
    def __init__(self, bundle_path: str = None):
        if bundle_path is None:
            bundle_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'model_data_bundle.joblib')
        if not os.path.exists(bundle_path):
            raise FileNotFoundError(f"Model data bundle not found at {bundle_path}")

        bundle = joblib.load(bundle_path)
        self.best_rf = bundle['best_rf']
        self.preprocessor = self.best_rf.named_steps['preprocessor']
        self.model = self.best_rf.named_steps['model']
        self.X_test = bundle['X_test_sel']

        raw_names = self.preprocessor.get_feature_names_out()
        self.clean_names = [f.replace('num__', '').replace('cat__', '') for f in raw_names]
        
        self.explainer = shap.TreeExplainer(self.model)
        self.base_value = float(
            self.explainer.expected_value[0]
            if isinstance(self.explainer.expected_value, (list, np.ndarray))
            else self.explainer.expected_value
        )

    def get_global_importance(self, n_samples: int = 100):
        X_trans = self.preprocessor.transform(self.X_test.iloc[:n_samples])
        shap_vals = self.explainer.shap_values(X_trans)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[0]

        mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
        df_imp = pd.DataFrame({
            'Feature': self.clean_names,
            'Mean_Abs_SHAP': mean_abs_shap
        }).sort_values(by='Mean_Abs_SHAP', ascending=False).reset_index(drop=True)
        return df_imp

    def explain_instance(self, single_row_df: pd.DataFrame, top_k: int = 8):
        X_trans = self.preprocessor.transform(single_row_df)
        pred_val = float(self.model.predict(X_trans)[0])
        shap_vals = self.explainer.shap_values(X_trans)
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[0]
        shap_row = shap_vals[0]

        impact_df = pd.DataFrame({
            'Feature': self.clean_names,
            'SHAP_Value': shap_row
        })

        pos_drivers = impact_df[impact_df['SHAP_Value'] > 0].sort_values(by='SHAP_Value', ascending=False).head(top_k)
        neg_drivers = impact_df[impact_df['SHAP_Value'] < 0].sort_values(by='SHAP_Value', ascending=True).head(top_k)

        summary_text = (
            f"The model predicts an expected yield of **{pred_val:.1f} Quintals/Acre** "
            f"(Regional Baseline: {self.base_value:.1f} Q/Acre).\n\n"
            f"**Key Growth Promoters (Yield Boosters):**\n"
            + "\n".join([f"- {r['Feature']}: +{r['SHAP_Value']:.1f} Q/Acre" for _, r in pos_drivers.head(3).iterrows()])
            + "\n\n**Key Limiting Factors (Yield Detractors):**\n"
            + "\n".join([f"- {r['Feature']}: {r['SHAP_Value']:.1f} Q/Acre" for _, r in neg_drivers.head(3).iterrows()])
        )

        return {
            'base_value': self.base_value,
            'predicted_value': pred_val,
            'positive_drivers': pos_drivers.to_dict(orient='records'),
            'negative_drivers': neg_drivers.to_dict(orient='records'),
            'summary_text': summary_text,
            'impact_df': impact_df
        }

    def create_plotly_waterfall(self, explanation_result: dict, max_display: int = 10):
        base_val = explanation_result['base_value']
        pred_val = explanation_result['predicted_value']
        pos = explanation_result['positive_drivers']
        neg = explanation_result['negative_drivers']

        combined = pos + neg
        combined.sort(key=lambda x: abs(x['SHAP_Value']), reverse=True)
        top_items = combined[:max_display]

        labels = ['Baseline Expected Yield'] + [item['Feature'] for item in top_items] + ['Final Predicted Yield']
        deltas = [base_val] + [item['SHAP_Value'] for item in top_items] + [0]
        measures = ['absolute'] + ['relative'] * len(top_items) + ['total']

        fig = go.Figure(go.Waterfall(
            name="SHAP Attribution",
            orientation="v",
            measure=measures,
            x=labels,
            textposition="outside",
            text=[f"{d:+.1f}" if m == 'relative' else f"{d:.1f}" for d, m in zip(deltas[:-1] + [pred_val], measures)],
            y=deltas[:-1] + [pred_val],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))
        fig.update_layout(
            title=f"SHAP Waterfall Attribution: Baseline ({base_val:.1f}) -> Predicted Yield ({pred_val:.1f} Q/Acre)",
            xaxis_title="Agro-Climatic Drivers",
            yaxis_title="Sugarcane Yield (Quintals/Acre)",
            template="plotly_white",
            height=480
        )
        return fig
