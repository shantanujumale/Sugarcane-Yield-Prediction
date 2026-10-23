import streamlit as st
import numpy as np
import pickle

# Load models
rf_model = pickle.load(open("rf_model.pkl", "rb"))
xgb_model = pickle.load(open("xgb_model.pkl", "rb"))
lr_model = pickle.load(open("lr_model.pkl", "rb"))
scaler = pickle.load(open("scaler_01.pkl", "rb"))

st.title("🎓 Student Performance Prediction (3 Models Comparison)")

# ==========================
# Inputs
# ==========================
age = st.number_input("Age", 15, 30, 18)
gender = st.selectbox("Gender", ["Male", "Female"])
study_hours = st.slider("Study Hours", 0, 12, 5)
attendance = st.slider("Attendance (%)", 0, 100, 75)

math = st.slider("Math Score", 0, 100, 70)
science = st.slider("Science Score", 0, 100, 70)
english = st.slider("English Score", 0, 100, 70)

overall = (math + science + english) / 3

# Encode (must match training)
gender_val = 1 if gender == "Male" else 0

input_data = np.array([[age, gender_val, study_hours, attendance,
                        math, science, english, overall]])

# Scale
input_scaled = scaler.transform(input_data)

# ==========================
# Prediction
# ==========================
if st.button("Predict"):

    rf_pred = rf_model.predict(input_scaled)[0]
    xgb_pred = xgb_model.predict(input_scaled)[0]
    lr_pred = lr_model.predict(input_scaled)[0]

    st.subheader("🔮 Predictions")

    st.write(f"Random Forest: **{rf_pred}**")
    st.write(f"XGBoost: **{xgb_pred}**")
    st.write(f"Logistic Regression: **{lr_pred}**")

    # ==========================
    # Comparison Logic
    # ==========================
    st.subheader("📊 Model Comparison")

    preds = [rf_pred, xgb_pred, lr_pred]

    if preds.count(preds[0]) == len(preds):
        st.success("All models agree ✅")
    else:
        st.warning("Models disagree ⚠️")

    # ==========================
    # Probability Comparison
    # ==========================
    st.subheader("📈 Prediction Confidence")

    st.write("Random Forest:", rf_model.predict_proba(input_scaled))
    st.write("XGBoost:", xgb_model.predict_proba(input_scaled))
    st.write("Logistic Regression:", lr_model.predict_proba(input_scaled))