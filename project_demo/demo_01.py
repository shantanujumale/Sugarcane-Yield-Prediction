import streamlit as st
import numpy as np
import pickle

# ==========================================
# Load Model & Scaler
# ==========================================
with open("student_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# ==========================================
# App Title
# ==========================================
st.title("🎓 Student Performance Prediction")
st.write("Enter student details to predict final performance")

# ==========================================
# Input Fields (Dataset Features)
# ==========================================
age = st.number_input("Age", 15, 30, 18)

gender = st.selectbox("Gender", ["Male", "Female"])
school_type = st.selectbox("School Type", ["Public", "Private"])
parent_education = st.selectbox("Parent Education", ["High School", "Bachelor", "Master"])

study_hours = st.slider("Study Hours", 0, 12, 5)
attendance = st.slider("Attendance (%)", 0, 100, 75)

internet = st.selectbox("Internet Access", ["No", "Yes"])
travel_time = st.slider("Travel Time", 0, 5, 2)

extra_activities = st.selectbox("Extra Activities", ["No", "Yes"])
study_method = st.selectbox("Study Method", ["Self", "Group"])

math_score = st.slider("Math Score", 0, 100, 70)
science_score = st.slider("Science Score", 0, 100, 70)
english_score = st.slider("English Score", 0, 100, 70)

overall_score = (math_score + science_score + english_score) / 3

# ==========================================
# Encode Inputs (IMPORTANT)
# ==========================================
def encode_inputs():
    return [
        age,
        1 if gender == "Male" else 0,
        1 if school_type == "Private" else 0,
        0 if parent_education == "High School" else (1 if parent_education == "Bachelor" else 2),
        study_hours,
        attendance,
        1 if internet == "Yes" else 0,
        travel_time,
        1 if extra_activities == "Yes" else 0,
        0 if study_method == "Self" else 1,
        math_score,
        science_score,
        english_score,
        overall_score
    ]

# ==========================================
# Prediction Button
# ==========================================
if st.button("Predict Performance"):

    input_data = np.array(encode_inputs()).reshape(1, -1)

    # Scale input
    input_scaled = scaler.transform(input_data)

    # Predict
    prediction = model.predict(input_scaled)

    # Display result
    st.subheader("Prediction Result:")

    if prediction[0] == 0:
        st.error("❌ Fail")
    elif prediction[0] == 1:
        st.warning("⚠️ Pass")
    else:
        st.success("🏆 Distinction")