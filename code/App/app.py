"""
Streamlit Decision-Support Web Application:
Maharashtra Sugarcane Yield Prediction and Agro-Resource Optimization Using Explainable Machine Learning
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure src modules can be imported
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from explainability import SugarcaneExplainer
from resource_optimizer import AgroResourceOptimizer

# Streamlit Page Config
st.set_page_config(
    page_title="Maharashtra Sugarcane Yield & Optimization",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4b6b50;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f1f8e9;
        border-left: 5px solid #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1b5e20;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Load Bundle and Model
@st.cache_resource
def load_artifacts():
    bundle_path = os.path.join(MODELS_DIR, 'model_data_bundle.joblib')
    if not os.path.exists(bundle_path):
        bundle_path = os.path.join(OUTPUT_DIR, 'model_data_bundle.joblib')
    if not os.path.exists(bundle_path):
        st.error(f"Model data bundle not found at {bundle_path}. Please run `python Code/run_pipeline.py` first.")
        return None, None, None

    explainer = SugarcaneExplainer(bundle_path)
    optimizer = AgroResourceOptimizer(bundle_path)
    bundle = joblib.load(bundle_path)
    return explainer, optimizer, bundle

explainer, optimizer, bundle = load_artifacts()

# App Header
st.markdown('<div class="main-header">🌾 Maharashtra Sugarcane Yield Prediction & Agro-Resource Optimization</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explainable Machine Learning Decision-Support System for Maharashtra Agro-Ecological Zones</div>', unsafe_allow_html=True)

if explainer is None or optimizer is None:
    st.stop()

# Load summary CSVs if available
def load_csv(filename):
    for d in [OUTPUT_DIR, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))]:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return pd.read_csv(p)
    return None

df_comparison = load_csv('model_comparison.csv')
df_cv = load_csv('cross_validation_results.csv')

# Sidebar: Farm Preset and Inputs
st.sidebar.header("🚜 Farm Configuration")

preset = st.sidebar.selectbox(
    "Choose Farm Preset / Profile:",
    ["Custom Farm", "Kolhapur (High Yield / Black Soil)", "Pune (Moderate Canal Irrigated)", "Solapur (Semi-Arid / Deficit)"]
)

# Reference sample row from test set
sample_row = explainer.X_test.iloc[0].copy()

# Preset parameter defaults
if preset == "Kolhapur (High Yield / Black Soil)":
    sample_row['District'] = 'Kolhapur'
    sample_row['Soil_Type'] = 'Black'
    sample_row['Cane_Height_cm'] = 295.0
    sample_row['Cane_Diameter_cm'] = 3.3
    sample_row['Soil_Moisture_%'] = 38.0
    sample_row['Water_Quantity_liters_per_acre'] = 1450.0
    sample_row['Fertilizer_Quantity'] = 220.0
elif preset == "Pune (Moderate Canal Irrigated)":
    sample_row['District'] = 'Pune'
    sample_row['Soil_Type'] = 'Alluvial'
    sample_row['Cane_Height_cm'] = 240.0
    sample_row['Cane_Diameter_cm'] = 2.8
    sample_row['Soil_Moisture_%'] = 29.0
    sample_row['Water_Quantity_liters_per_acre'] = 1200.0
    sample_row['Fertilizer_Quantity'] = 180.0
elif preset == "Solapur (Semi-Arid / Deficit)":
    sample_row['District'] = 'Solapur'
    sample_row['Soil_Type'] = 'Red'
    sample_row['Cane_Height_cm'] = 180.0
    sample_row['Cane_Diameter_cm'] = 2.2
    sample_row['Soil_Moisture_%'] = 20.0
    sample_row['Water_Quantity_liters_per_acre'] = 900.0
    sample_row['Fertilizer_Quantity'] = 140.0

st.sidebar.markdown("---")
st.sidebar.subheader("Key Field Parameters")

district_val = sample_row.get('District', 'Kolhapur')
district_list = ['Ahmednagar', 'Kolhapur', 'Pune', 'Sangli', 'Satara', 'Solapur']
dist_idx = district_list.index(district_val) if district_val in district_list else 0
sel_district = st.sidebar.selectbox("District", district_list, index=dist_idx)

cane_height = st.sidebar.slider("Cane Height (cm)", 100.0, 400.0, float(sample_row.get('Cane_Height_cm', 250.0)), 5.0)
cane_diam = st.sidebar.slider("Cane Diameter (cm)", 1.5, 4.5, float(sample_row.get('Cane_Diameter_cm', 2.8)), 0.1)
soil_moist = st.sidebar.slider("Soil Moisture (%)", 10.0, 50.0, float(sample_row.get('Soil_Moisture_%', 28.0)), 1.0)
water_qty = st.sidebar.slider("Water Quantity (Liters/Acre)", 600.0, 2000.0, float(sample_row.get('Water_Quantity_liters_per_acre', 1200.0)), 25.0)
fert_qty = st.sidebar.slider("Fertilizer Quantity (kg/Acre)", 80.0, 350.0, float(sample_row.get('Fertilizer_Quantity', 180.0)), 5.0)

# Build modified row
farmer_data = sample_row.copy()
if 'District' in farmer_data:
    farmer_data['District'] = sel_district
if 'Cane_Height_cm' in farmer_data:
    farmer_data['Cane_Height_cm'] = cane_height
if 'Cane_Diameter_cm' in farmer_data:
    farmer_data['Cane_Diameter_cm'] = cane_diam
if 'Soil_Moisture_%' in farmer_data:
    farmer_data['Soil_Moisture_%'] = soil_moist
if 'Water_Quantity_liters_per_acre' in farmer_data:
    farmer_data['Water_Quantity_liters_per_acre'] = water_qty
if 'Fertilizer_Quantity' in farmer_data:
    farmer_data['Fertilizer_Quantity'] = fert_qty

# Update engineered interactions if present
if 'Cane_Growth_Index' in farmer_data:
    farmer_data['Cane_Growth_Index'] = cane_height * cane_diam
if 'Fertilizer_Irrigation' in farmer_data:
    farmer_data['Fertilizer_Irrigation'] = fert_qty * water_qty

farmer_df = pd.DataFrame([farmer_data])

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌾 Yield Prediction",
    "🔍 Explainable AI (SHAP)",
    "💧 What-If Agro Scenarios",
    "🎯 Agro-Resource Optimization",
    "📊 Benchmarks & Accuracy"
])

# -------------------------------------------------------------
# TAB 1: YIELD PREDICTION
# -------------------------------------------------------------
with tab1:
    st.subheader("🌾 Crop Yield Forecast")
    
    # Predict using Champion Pipeline
    pipe = bundle['champion_pipeline']
    expected_cols = bundle['selected_numeric'] + bundle['selected_categorical']
    pred_yield = float(pipe.predict(farmer_df[expected_cols])[0])
    pred_tonnes_ha = pred_yield * 0.2471  # 1 Quintal/Acre = 24.71 Q/ha = 2.471 Tonnes/ha
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Predicted Sugarcane Yield</div>
            <div class="metric-val">{pred_yield:.2f} <span style="font-size:1rem;color:#333;">Q / Acre</span></div>
            <div style="font-size:0.85rem;color:#666;">Quintals per Acre</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Metric Equivalent</div>
            <div class="metric-val">{pred_tonnes_ha:.2f} <span style="font-size:1rem;color:#333;">Tonnes / Ha</span></div>
            <div style="font-size:0.85rem;color:#666;">Tonnes per Hectare</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        baseline_avg = float(explainer.base_value)
        diff = pred_yield - baseline_avg
        diff_str = f"+{diff:.1f}" if diff >= 0 else f"{diff:.1f}"
        diff_color = "#2e7d32" if diff >= 0 else "#c62828"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Comparison to Maharashtra Average</div>
            <div class="metric-val" style="color:{diff_color};">{diff_str} <span style="font-size:1rem;color:#333;">Q / Acre</span></div>
            <div style="font-size:0.85rem;color:#666;">Baseline: {baseline_avg:.1f} Q/Acre</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📅 Crop Lifecycle Progression (F1 → F2 → F3)")
    st.write(
        "Demonstrating how predictive accuracy evolves across the crop lifecycle without temporal leakage:"
    )
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.info("**F1: Early-Stage (Pre-Season)**\n- Soil, Climate, Planning\n- 5-Fold CV $R^2$: **0.3256**\n- CV MAE: **69.99 Q/Acre**")
    with col_f2:
        st.success("**F2: Mid-Season (Tillering)**\n- + Germination, Tillering, Pest\n- 5-Fold CV $R^2$: **0.8184**\n- CV MAE: **34.07 Q/Acre**")
    with col_f3:
        st.success("**F3: Late-Season (Maturity)**\n- + Cane Height, Diameter, Brix\n- 5-Fold CV $R^2$: **0.8171**\n- Tuned XGBoost $R^2$: **0.8716**")

# -------------------------------------------------------------
# TAB 2: EXPLAINABLE AI (SHAP)
# -------------------------------------------------------------
with tab2:
    st.subheader("🔍 Explainable AI: Feature Attribution Analysis")
    st.write(
        "SHAP (SHapley Additive exPlanations) explains exactly why the model made this specific prediction, "
        "quantifying the contribution of each agronomic, soil, and management factor."
    )

    col_sh1, col_sh2 = st.columns([1, 1])

    with col_sh1:
        st.markdown("#### 🌟 Individual Farm Waterfall Attribution")
        explanation = explainer.explain_instance(farmer_df[expected_cols], top_k=8)
        st.write(f"**Predicted Yield:** `{explanation['prediction']:.2f} Q/Acre` | **Baseline:** `{explanation['base_value']:.2f} Q/Acre`")

        df_waterfall = explanation['waterfall_df']
        fig, ax = plt.subplots(figsize=(7, 4.5))
        colors = ['#2e7d32' if v >= 0 else '#c62828' for v in df_waterfall['SHAP_Value']]
        ax.barh(df_waterfall['Feature'], df_waterfall['SHAP_Value'], color=colors)
        ax.axvline(0, color='black', linestyle='--', linewidth=0.8)
        ax.set_xlabel('SHAP Attribution (Quintal/Acre Impact)')
        ax.set_title('Top Driving Factors for Current Farm')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)

    with col_sh2:
        st.markdown("#### 📈 Global Feature Importance (Maharashtra-Wide)")
        df_glob = explainer.get_global_importance(n_samples=100).head(8)
        fig_glob, ax_glob = plt.subplots(figsize=(7, 4.5))
        ax_glob.barh(df_glob['Feature'], df_glob['Mean_Abs_SHAP'], color='#1565c0')
        ax_glob.set_xlabel('Mean |SHAP Value| (Impact on Yield)')
        ax_glob.set_title('Top 8 Decisive Predictors Across All Regions')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig_glob)

    st.markdown("---")
    st.subheader("Agronomic Insights & Recommendations")
    st.write(explanation['interpretation'])

# -------------------------------------------------------------
# TAB 3: WHAT-IF SCENARIOS
# -------------------------------------------------------------
with tab3:
    st.subheader("💧 What-If Agro-Resource Scenarios")
    st.write(
        "Examine how systemic changes in irrigation and fertilization policies impact expected sugarcane harvest:"
    )

    df_scenarios = optimizer.run_what_if_scenarios(farmer_data)
    st.dataframe(df_scenarios, use_container_width=True)

    fig_sc, ax_sc = plt.subplots(figsize=(10, 4))
    sns.barplot(
        data=df_scenarios,
        x='Scenario',
        y='Predicted Yield (Q/Acre)',
        palette='Greens_d',
        ax=ax_sc
    )
    ax_sc.set_xticklabels(ax_sc.get_xticklabels(), rotation=20, ha='right')
    ax_sc.set_title('Predicted Yield Across 5 Agronomic Resource Regimes')
    plt.tight_layout()
    st.pyplot(fig_sc)

# -------------------------------------------------------------
# TAB 4: CONSTRAINED AGRO-RESOURCE OPTIMIZATION
# -------------------------------------------------------------
with tab4:
    st.subheader("🎯 Constrained Agro-Resource Optimization Engine")
    st.write(
        "Find the mathematically optimal combination of Water and Fertilizer to maximize yield subject to farm quotas:"
    )

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        max_water_quota = st.slider("Maximum Water Quota (Liters/Acre)", 800.0, 2000.0, 1500.0, 50.0)
    with col_opt2:
        max_fert_quota = st.slider("Maximum Fertilizer Quota (kg/Acre)", 100.0, 350.0, 250.0, 10.0)

    if st.button("🚀 Run SLSQP Constrained Optimization", type="primary"):
        with st.spinner("Optimizing input allocation..."):
            opt_res = optimizer.optimize_resources(
                farmer_data,
                water_bounds=(700.0, max_water_quota),
                fert_bounds=(100.0, max_fert_quota)
            )

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Optimal Water Quantity", f"{opt_res['Optimal_Water_L_per_Acre']:.1f} L/Acre")
        with col_r2:
            st.metric("Optimal Fertilizer", f"{opt_res['Optimal_Fertilizer_kg_per_Acre']:.1f} kg/Acre")
        with col_r3:
            st.metric("Maximum Achievable Yield", f"{opt_res['Max_Predicted_Yield']:.2f} Q/Acre", delta=f"{opt_res['Yield_Gain_Q_per_Acre']:+.2f} Q/Acre")

        st.success(
            f"**Optimization Recommendation:** By tuning water to **{opt_res['Optimal_Water_L_per_Acre']:.1f} L/Acre** "
            f"and fertilizer to **{opt_res['Optimal_Fertilizer_kg_per_Acre']:.1f} kg/Acre**, predicted harvest increases by "
            f"**{opt_res['Yield_Gain_Q_per_Acre']:.2f} Q/Acre** ({opt_res['Yield_Gain_Percent']:+.1f}%) compared to baseline!"
        )

# -------------------------------------------------------------
# TAB 5: BENCHMARKS & MODEL ACCURACY
# -------------------------------------------------------------
with tab5:
    st.subheader("📊 Rigorous Model Benchmarking & Validation")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("#### 🏆 Final Model Evaluation (Untouched 20% Test Set)")
        if df_comparison is not None:
            st.dataframe(df_comparison, use_container_width=True)
        else:
            st.write("Run pipeline to view updated comparison table.")

    with col_b2:
        st.markdown("#### 🔄 5-Fold Cross-Validation on Training Set")
        if df_cv is not None:
            st.dataframe(df_cv, use_container_width=True)
        else:
            st.write("Run pipeline to view cross-validation results.")

    st.markdown("---")
    st.markdown("### 🏆 Champion Architecture: Tuned XGBoost Regressor")
    st.write(
        "- **Test $R^2$:** `0.8716` (Explains 87.16% of yield variance on unseen Maharashtra farm data)\n"
        "- **Test MAE:** `29.33 Quintal/Acre`\n"
        "- **Test RMSE:** `38.20 Quintal/Acre`\n"
        "- **Validation:** 5-Fold Cross-Validation with strict train-only preprocessing to prevent target and distribution leakage."
    )
