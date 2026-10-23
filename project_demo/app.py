import pickle

import numpy as np
import streamlit as st


st.set_page_config(
    page_title="Student Performance Prediction",
    page_icon="🎓",
    layout="wide",
)


# ==========================================
# Load Model & Scaler
# ==========================================
with open("student_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)


def inject_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        :root {
            --bg: #f4f8fb;
            --panel: rgba(255, 255, 255, 0.88);
            --panel-strong: #ffffff;
            --text: #15304a;
            --muted: #5f7285;
            --primary: #0f9d8a;
            --secondary: #0f6cbd;
            --accent: #f9a826;
            --border: rgba(21, 48, 74, 0.12);
            --shadow: 0 20px 45px rgba(15, 108, 189, 0.12);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 157, 138, 0.18), transparent 24%),
                radial-gradient(circle at top right, rgba(249, 168, 38, 0.18), transparent 22%),
                linear-gradient(180deg, #eef6fb 0%, #f7fbff 45%, #f4f8fb 100%);
            color: var(--text);
            font-family: 'Poppins', sans-serif;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, label, p, div {
            font-family: 'Poppins', sans-serif !important;
        }

        [data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
        }

        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            gap: 1rem;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(15, 108, 189, 0.96), rgba(15, 157, 138, 0.88));
            color: #ffffff;
            border-radius: 28px;
            padding: 2rem 2.2rem;
            box-shadow: 0 24px 60px rgba(15, 108, 189, 0.22);
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            width: 220px;
            height: 220px;
            right: -80px;
            top: -80px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.12);
        }

        .hero-kicker {
            font-size: 0.85rem;
            letter-spacing: 0.14rem;
            text-transform: uppercase;
            font-weight: 600;
            opacity: 0.85;
            margin-bottom: 0.7rem;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 0.7rem;
            max-width: 760px;
        }

        .hero-subtitle {
            font-size: 1rem;
            line-height: 1.75;
            opacity: 0.95;
            max-width: 760px;
            margin-bottom: 0;
        }

        .section-card {
            background: var(--panel);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.1rem 1.2rem 1.35rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .section-title {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0 0 0.2rem 0;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 0.92rem;
            margin: 0 0 0.2rem 0;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(248,252,255,0.96));
            border: 1px solid rgba(15, 108, 189, 0.12);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 16px 30px rgba(21, 48, 74, 0.08);
            min-height: 120px;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            color: var(--text);
            font-size: 1.9rem;
            font-weight: 700;
            margin: 0;
        }

        .metric-note {
            color: var(--secondary);
            font-size: 0.9rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }

        .stNumberInput, .stSelectbox, .stSlider {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 18px;
            padding: 0.2rem 0.3rem;
        }

        div[data-baseweb="select"] > div,
        .stNumberInput div[data-baseweb="input"] > div {
            border-radius: 14px !important;
            border: 1px solid rgba(15, 108, 189, 0.18) !important;
            min-height: 46px;
        }

        .stSlider [data-baseweb="slider"] {
            padding-top: 0.6rem;
            padding-bottom: 0.3rem;
        }

        .stButton > button {
            width: 100%;
            border: none;
            border-radius: 16px;
            padding: 0.95rem 1.2rem;
            background: linear-gradient(135deg, #0f6cbd, #0f9d8a);
            color: white;
            font-size: 1rem;
            font-weight: 700;
            box-shadow: 0 18px 30px rgba(15, 108, 189, 0.25);
            transition: all 0.2s ease-in-out;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 22px 36px rgba(15, 108, 189, 0.3);
        }

        .result-card {
            background: linear-gradient(145deg, #ffffff, #f5fbff);
            border: 1px solid rgba(15, 157, 138, 0.18);
            border-radius: 24px;
            padding: 1.3rem;
            box-shadow: var(--shadow);
            margin-top: 1rem;
        }

        .result-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.3rem;
        }

        .result-caption {
            color: var(--muted);
            margin-bottom: 0.8rem;
        }

        @media (max-width: 768px) {
            .hero-title {
                font-size: 1.8rem;
            }

            .block-container {
                padding-top: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
        overall_score,
    ]


def get_prediction_display(predicted_value):
    normalized_text = str(predicted_value).strip().lower()

    label_map = {
        "0": ("Fail", "The model predicts that this student may fail without additional support.", "error"),
        "0.0": ("Fail", "The model predicts that this student may fail without additional support.", "error"),
        "fail": ("Fail", "The model predicts that this student may fail without additional support.", "error"),
        "at risk": ("Fail", "The model predicts that this student may fail without additional support.", "error"),
        "1": ("Pass", "The student is likely to pass, but there is room to strengthen performance.", "warning"),
        "1.0": ("Pass", "The student is likely to pass, but there is room to strengthen performance.", "warning"),
        "pass": ("Pass", "The student is likely to pass, but there is room to strengthen performance.", "warning"),
        "2": ("Distinction", "The student is on track for excellent academic performance.", "success"),
        "2.0": ("Distinction", "The student is on track for excellent academic performance.", "success"),
        "distinction": ("Distinction", "The student is on track for excellent academic performance.", "success"),
    }

    if normalized_text in label_map:
        return label_map[normalized_text]

    try:
        numeric_value = int(float(normalized_text))
    except ValueError:
        return (
            "Prediction Available",
            f"The model returned: {predicted_value}",
            "info",
        )

    numeric_map = {
        0: ("Fail", "The model predicts that this student may fail without additional support.", "error"),
        1: ("Pass", "The student is likely to pass, but there is room to strengthen performance.", "warning"),
        2: ("Distinction", "The student is on track for excellent academic performance.", "success"),
    }
    return numeric_map.get(
        numeric_value,
        ("Prediction Available", f"The model returned: {predicted_value}", "info"),
    )


inject_styles()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">AI Academic Dashboard</div>
        <div class="hero-title">Student Performance Prediction</div>
        <p class="hero-subtitle">
            Enter a student's academic and lifestyle details to predict the final performance level.
        
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1.7, 1], gap="large")

with left_col:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Student Profile</div>
            <div class="section-subtitle">Basic details and learning environment</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", 15, 30, 18)
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col3:
        school_type = st.selectbox("School Type", ["Public", "Private"])

    col4, col5 = st.columns(2)
    with col4:
        parent_education = st.selectbox("Parent Education", ["High School", "Bachelor", "Master"])
    with col5:
        internet = st.selectbox("Internet Access", ["No", "Yes"])

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Habits & Engagement</div>
            <div class="section-subtitle">Study patterns, attendance, and activities</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col6, col7 = st.columns(2)
    with col6:
        study_hours = st.slider("Study Hours", 0, 12, 5)
        travel_time = st.slider("Travel Time", 0, 5, 2)
    with col7:
        attendance = st.slider("Attendance (%)", 0, 100, 75)
        extra_activities = st.selectbox("Extra Activities", ["No", "Yes"])

    study_method = st.selectbox("Study Method", ["Self", "Group"])

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Subject Scores</div>
            <div class="section-subtitle">Set the current marks to estimate performance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col8, col9, col10 = st.columns(3)
    with col8:
        math_score = st.slider("Math Score", 0, 100, 70)
    with col9:
        science_score = st.slider("Science Score", 0, 100, 70)
    with col10:
        english_score = st.slider("English Score", 0, 100, 70)

with right_col:
    overall_score = (math_score + science_score + english_score) / 3

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <p class="metric-value">{overall_score:.1f}</p>
            <div class="metric-note">Live preview based on entered marks</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Attendance Level</div>
            <p class="metric-value">{attendance}%</p>
            <div class="metric-note">Study hours: {study_hours} hrs/day</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Learning Style</div>
            <p class="metric-value">{study_method}</p>
            <div class="metric-note">Travel time: {travel_time} hour(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    predict_clicked = st.button("Predict Performance")


if predict_clicked:
    input_data = np.array(encode_inputs()).reshape(1, -1)
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)
    result_title, result_text, result_type = get_prediction_display(prediction[0])

    st.markdown(
        """
        <div class="result-card">
            <div class="result-title">Prediction Result</div>
            <div class="result-caption">Model output based on the current student profile</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result_type == "error":
        st.error(f"{result_title}: {result_text}")
    elif result_type == "warning":
        st.warning(f"{result_title}: {result_text}")
    elif result_type == "success":
        st.success(f"{result_title}: {result_text}")
    else:
        st.info(f"{result_title}: {result_text}")


# python -m streamlit run app.py
