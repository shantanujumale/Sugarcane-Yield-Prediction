"""
Interactive Streamlit Web Application: Sugarcane Yield Prediction System
Symbiosis Institute of Technology (SIT) - Semester 5 Academic Project
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="Sugarcane Yield Prediction | Maharashtra",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e5631;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4f6d7a;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #2d6a4f;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.08);
    }
    .badge-high {
        background-color: #d8f3dc;
        color: #1b4332;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'best_sugarcane_model.pkl')
METADATA_PATH = os.path.join(BASE_DIR, 'model_metadata.json')
BENCHMARK_PATH = os.path.join(BASE_DIR, 'model_benchmark_results.csv')

@st.cache_resource
def load_model_and_metadata():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(METADATA_PATH):
        return None, None
    model = joblib.load(MODEL_PATH)
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return model, meta

model, metadata = load_model_and_metadata()

# Sidebar
st.sidebar.image("https://images.unsplash.com/photo-1593113598332-cd288d649433?w=500&auto=format&fit=crop&q=60", use_container_width=True)
st.sidebar.title("🌾 Navigation")
page = st.sidebar.radio("Go to:", ["🌱 Real-Time Yield Predictor", "📊 Model Performance Dashboard", "📖 Project Documentation"])

st.sidebar.markdown("---")
st.sidebar.info("""
**Project**: Sugarcane Yield Prediction Using ML  
**State Focus**: Maharashtra Districts  
**Algorithms**: Linear Regression, Decision Tree, Random Forest, XGBoost  
**Target Metric**: Quintals per Acre
""")

if model is None:
    st.error("⚠️ Model artifacts not found. Please run `python train_models.py` to train and save the models first.")
    st.stop()

# ==========================================
# PAGE 1: PREDICTOR
# ==========================================
if page == "🌱 Real-Time Yield Predictor":
    st.markdown('<div class="main-title">🌾 Sugarcane Crop Yield Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Predict sugarcane crop productivity across Maharashtra districts based on soil, climatic, and crop parameters.</div>', unsafe_allow_html=True)

    cat_mappings = metadata.get('cat_mappings', {})
    district_list = cat_mappings.get('District', {}).get('classes', [
        'Ahmednagar', 'Aurangabad', 'Beed', 'Jalgaon', 'Jalna', 'Kolhapur',
        'Latur', 'Nanded', 'Nashik', 'Osmanabad', 'Pune', 'Sangli', 'Satara', 'Solapur'
    ])

    with st.form("prediction_form"):
        tab1, tab2, tab3, tab4 = st.tabs([
            "📍 Region & Season", 
            "🧪 Soil & Nutrition", 
            "🌦️ Climate & Weather", 
            "🚜 Growth & Farm Practices"
        ])

        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                district = st.selectbox("Select Maharashtra District", district_list, index=district_list.index('Kolhapur') if 'Kolhapur' in district_list else 0)
            with col2:
                season = st.selectbox("Season", ['Kharif', 'Rabi'])
            with col3:
                growth_stage = st.selectbox("Growth Stage", ['Mid', 'Late', 'Early'])

        with tab2:
            col1, col2, col3 = st.columns(3)
            with col1:
                soil_type = st.selectbox("Soil Type", ['Clay', 'Loamy', 'Alluvial', 'Sandy'])
                soil_ph = st.slider("Soil pH", 4.5, 9.5, 7.2, 0.1)
                soil_moisture = st.slider("Soil Moisture (%)", 10.0, 60.0, 32.5, 0.5)
            with col2:
                nitrogen = st.number_input("Nitrogen (kg/acre)", min_value=10.0, max_value=300.0, value=145.0, step=5.0)
                phosphorus = st.number_input("Phosphorus (kg/acre)", min_value=5.0, max_value=150.0, value=55.0, step=5.0)
                potassium = st.number_input("Potassium (kg/acre)", min_value=10.0, max_value=250.0, value=110.0, step=5.0)
            with col3:
                ec = st.number_input("Electrical Conductivity (EC dS/m)", 0.1, 5.0, 1.2, 0.1)
                organic_carbon = st.slider("Organic Carbon (%)", 0.1, 3.0, 1.1, 0.1)
                drainage = st.selectbox("Drainage Condition", ['Good', 'Moderate', 'Poor'])

        with tab3:
            col1, col2, col3 = st.columns(3)
            with col1:
                temp_avg = st.slider("Average Temperature (°C)", 15.0, 45.0, 29.5, 0.5)
                rainfall = st.number_input("Total Rainfall (mm)", min_value=200.0, max_value=3000.0, value=1250.0, step=50.0)
            with col2:
                humidity = st.slider("Humidity (%)", 20.0, 95.0, 72.0, 1.0)
                wind_speed = st.slider("Wind Speed (km/h)", 2.0, 35.0, 12.0, 0.5)
            with col3:
                heat_stress = st.number_input("Heat Stress Days", min_value=0, max_value=60, value=12)
                frost_days = st.number_input("Frost Days", min_value=0, max_value=15, value=0)

        with tab4:
            col1, col2, col3 = st.columns(3)
            with col1:
                variety = st.selectbox("Sugarcane Variety", ['Co0238', 'CoJ64', 'Co98014'])
                planting_method = st.selectbox("Planting Method", ['Paired Row', 'Straight Row', 'Trench', 'Circular'])
                irrigation_method = st.selectbox("Irrigation Method", ['Drip', 'Flood', 'Sprinkler'])
            with col2:
                irrigation_freq = st.selectbox("Irrigation Frequency", ['Medium', 'High', 'Low'])
                water_quality = st.selectbox("Irrigation Water Quality", ['Good', 'Moderate', 'Saline'])
                fertilizer_type = st.selectbox("Primary Fertilizer", ['Urea', 'DAP', 'Organic'])
            with col3:
                cane_height = st.number_input("Cane Height (cm)", min_value=50.0, max_value=450.0, value=265.0, step=5.0)
                cane_diameter = st.number_input("Cane Diameter (cm)", min_value=1.5, max_value=6.0, value=3.8, step=0.1)
                brix_val = st.slider("Brix Value (°Bx Sugar Content)", 10.0, 26.0, 20.5, 0.5)
                disease_sev = st.selectbox("Disease Severity", ['None', 'Low', 'Medium', 'High'])
                pest_level = st.selectbox("Pest Level", ['Low', 'Medium', 'High'])

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚜 Calculate Sugarcane Yield Prediction", use_container_width=True)

    if submit_btn:
        input_data = {
            'District': district,
            'Season': season,
            'Growth_Stage': growth_stage,
            'Soil_Type': soil_type,
            'Soil_pH': soil_ph,
            'Soil_Moisture_%': soil_moisture,
            'Nitrogen_kg_per_acre': nitrogen,
            'Phosphorus_kg_per_acre': phosphorus,
            'Potassium_kg_per_acre': potassium,
            'EC': ec,
            'Organic_Carbon_%': organic_carbon,
            'Drainage_Condition': drainage,
            'Temp_Avg_C': temp_avg,
            'Rainfall_Total_mm': rainfall,
            'Humidity_%': humidity,
            'Wind_Speed_kmph': wind_speed,
            'Heat_Stress_Days': heat_stress,
            'Frost_Days': frost_days,
            'Variety': variety,
            'Planting_Method': planting_method,
            'Irrigation_Method_Type': irrigation_method,
            'Irrigation_Frequency_Level': irrigation_freq,
            'Water_Quality_Category': water_quality,
            'Fertilizer_Type': fertilizer_type,
            'Cane_Height_cm': cane_height,
            'Cane_Diameter_cm': cane_diameter,
            'Brix_Value': brix_val,
            'Disease_Severity': disease_sev,
            'Pest_Level': pest_level
        }

        # Build feature vector
        feature_names = metadata['feature_names']
        num_medians = metadata['num_medians']
        cat_map = metadata['cat_mappings']

        row = {}
        for feat in feature_names:
            if feat in input_data and input_data[feat] is not None:
                val = input_data[feat]
                if feat in cat_map:
                    row[feat] = cat_map[feat]['mapping'].get(str(val), 0)
                else:
                    try:
                        row[feat] = float(val)
                    except:
                        row[feat] = num_medians.get(feat, 0.0)
            else:
                if feat in cat_map:
                    row[feat] = cat_map[feat]['mapping'].get(cat_map[feat]['default'], 0)
                else:
                    row[feat] = num_medians.get(feat, 0.0)

        df_input = pd.DataFrame([row])[feature_names]
        predicted_yield = float(model.predict(df_input)[0])
        predicted_yield = max(10.0, round(predicted_yield, 2))
        ton_per_ha = round(predicted_yield * 0.2471, 2)
        metric_ton_per_acre = round(predicted_yield * 0.1, 2)

        st.success("✅ Prediction Generated Successfully!")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="🌾 Predicted Yield (Quintal/Acre)", value=f"{predicted_yield} Qtl/Acre")
        with c2:
            st.metric(label="🚜 Predicted Yield (Metric Tons/Acre)", value=f"{metric_ton_per_acre} Tons/Acre")
        with c3:
            st.metric(label="🌍 Predicted Yield (Metric Tons/Hectare)", value=f"{ton_per_ha} Tons/Ha")

        # Yield Category & Agronomic Insights
        st.markdown("### 📋 Agronomic Assessment & Advisory")
        if predicted_yield > 320:
            st.markdown(f"🌟 **Optimal High Yield**: Your forecasted yield in **{district}** is outstanding! Recommended actions: Maintain drip irrigation schedules and monitor ripening stage sugar (°Bx) accumulation.")
        elif predicted_yield >= 220:
            st.markdown(f"🌿 **Good Moderate Yield**: Healthy crop performance in **{district}**. Consider optimizing NPK top-dressing and weed management to push yield above 300 Quintals/Acre.")
        else:
            st.markdown(f"⚠️ **Below Average Yield Warning**: Forecasted yield in **{district}** indicates stress factors. Check for soil moisture deficit, NPK nutrient imbalances, or pest/disease severity.")

# ==========================================
# PAGE 2: DASHBOARD
# ==========================================
elif page == "📊 Model Performance Dashboard":
    st.markdown('<div class="main-title">📊 ML Model Benchmarking & Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Comparative performance of Linear Regression, Decision Tree, Random Forest, and XGBoost on unseen test data.</div>', unsafe_allow_html=True)

    if os.path.exists(BENCHMARK_PATH):
        results_df = pd.read_csv(BENCHMARK_PATH)
        
        st.markdown("### 🏆 Algorithm Comparison Table")
        st.dataframe(results_df.style.highlight_max(subset=['Test R2'], color='#d8f3dc')
                                   .highlight_min(subset=['Test MAE', 'Test RMSE'], color='#d8f3dc'),
                     use_container_width=True)

        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            fig, ax = plt.subplots(figsize=(7, 4.5))
            sns.barplot(data=results_df, x='Model', y='Test R2', palette='viridis', ax=ax)
            ax.set_title('Test R² Score Comparison (Higher is Better)', fontweight='bold')
            ax.set_ylim(0, 1.0)
            for p in ax.patches:
                ax.annotate(f"{p.get_height():.3f}", (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                            ha='center', va='center', color='white', fontweight='bold')
            st.pyplot(fig)

        with c2:
            fig, ax = plt.subplots(figsize=(7, 4.5))
            melted = results_df.melt(id_vars=['Model'], value_vars=['Test MAE', 'Test RMSE'], 
                                     var_name='Metric', value_name='Error')
            sns.barplot(data=melted, x='Model', y='Error', hue='Metric', palette='rocket', ax=ax)
            ax.set_title('Error Metrics (MAE & RMSE in Qtl/Acre)', fontweight='bold')
            st.pyplot(fig)

        # Feature Importance Chart
        feat_chart_path = os.path.join(BASE_DIR, 'feature_importance.png')
        if os.path.exists(feat_chart_path):
            st.markdown("---")
            st.markdown("### 🔍 Top Feature Importances (XGBoost)")
            st.image(feat_chart_path, use_container_width=True)
    else:
        st.warning("Benchmark results file not found. Run `python train_models.py`.")

# ==========================================
# PAGE 3: DOCUMENTATION
# ==========================================
elif page == "📖 Project Documentation":
    st.markdown('<div class="main-title">📖 Project Architecture & Methodology</div>', unsafe_allow_html=True)
    st.markdown("""
    ### Symbiosis Institute of Technology (SIT) - Sem 5 Academic Project
    **Topic**: Sugarcane Crop Yield Prediction Using Machine Learning
    
    #### 1. Why Maharashtra State Focus?
    Maharashtra is India's leading commercial sugarcane and sugar-producing state. Sugarcane productivity varies significantly across agro-climatic zones:
    - **Western Maharashtra (Kolhapur, Sangli, Satara, Pune, Solapur, Ahmednagar)**: Sugar bowl of Maharashtra with high productivity and cooperative sugar mills.
    - **Marathwada (Latur, Beed, Osmanabad, Nanded, Jalna, Aurangabad)**: High solar radiation, semi-arid conditions, reliant on canal and groundwater irrigation.
    - **North Maharashtra (Nashik, Jalgaon)**: Sub-tropical sugarcane cultivation.
    
    #### 2. Resolving Data Leakage & Overfitting
    - **The 99% Accuracy Trap**: Using `Production` alongside `Area` creates mathematical target leakage since $\text{Yield} = \text{Production} / \text{Area}$. We eliminated all leakage features.
    - **Realistic Evaluation**: We used an 80/20 train/test split. XGBoost achieved a realistic and scientifically credible **$R^2$ of ~89.8%** on unseen test data without memorizing labels.
    
    #### 3. Evaluation Metrics Used
    - **MAE (Mean Absolute Error)**: Average absolute magnitude of prediction error in Quintals/Acre.
    - **MSE (Mean Squared Error)**: Penalizes large deviations.
    - **RMSE (Root Mean Squared Error)**: Standard deviation of residuals.
    - **$R^2$ (Coefficient of Determination)**: Proportion of variance explained by environmental and agricultural features.
    """)
