import streamlit as st
from health_recommendation_agent import UserInput
from main import analyze_conditions, get_api_keys, get_notification_config

COLORS = {
  "primary": "#2B4A7A",      
  "secondary": "#F5F5DC",    
  "accent": "#E6F0FA",       
  "highlight": "#DAD7B5",    
  "text_dark": "#222222",
  "white": "#FFFFFF"
}
st.set_page_config(page_title="AQI Health Analyzer", page_icon="🌍", layout="centered")
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLORS['accent']};
        }}
        .main-title {{
            color: {COLORS['primary']};
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
        }}
        .subtitle {{
            color: {COLORS['secondary']};
            font-size: 1.2rem;
            text-align: center;
        }}
        .stButton>button {{
            background-color: {COLORS['primary']};
            color: {COLORS['white']};
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AQI Health Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Get air quality, health recommendations, and pollution news</div>', unsafe_allow_html=True)

with st.form("user_input_form"):
    city = st.text_input("City", "Delhi")
    state = st.text_input("State", "Delhi")
    country = st.text_input("Country", "India")
    medical_conditions = st.text_input("Medical Conditions (optional)")
    planned_activity = st.text_input("Planned Activity", "Morning walk")
    submitted = st.form_submit_button("Analyze")

if submitted:
    st.info("Analyzing conditions...", icon="🔎")
    user_input = UserInput(
        city=city,
        state=state,
        country=country,
        medical_conditions=medical_conditions,
        planned_activity=planned_activity
    )
    API_KEYS = get_api_keys()
    NOTIFICATION_CONFIG = get_notification_config()
    recommendations, news_summary, hospital_plan, alert_needed, alert_level, reason = analyze_conditions(
        user_input=user_input,
        api_keys=API_KEYS,
        healthcare_api_data={},
        epidemic_signal=None,
        resource_status=None,
        notification_config=NOTIFICATION_CONFIG
    )
    st.subheader("📰 Recent Pollution News")
    st.markdown(news_summary)
    st.subheader("✅ Health Recommendations")
    st.markdown(recommendations)
    st.subheader("🏥 Hospital Planning Actions")
    st.markdown(hospital_plan)
    # SMS Alert status
    if alert_needed:
        st.success(f"🚨 SMS Alert Sent! Level: {alert_level.value.upper()} | Reason: {reason}")
    else:
        st.info("No SMS alert needed based on current assessment.")
    # Satisfaction feedback
    st.markdown("---")
    st.subheader("📊 Feedback & Satisfaction Survey")
    feedback = st.radio("Are you satisfied with the AI-generated report and alerting?", ["Yes", "No", "Partially"], index=0)
    comments = st.text_area("Additional comments or suggestions:")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
    # Download button with detailed agentic report
    output_text = f"Agentic AI Hospital Surge Management Report\n\nLocation: {city}, {state}, {country}\nPlanned Activity: {planned_activity}\nMedical Conditions: {medical_conditions or 'None'}\n\n---\nRecent Pollution News:\n{news_summary}\n\nHealth Recommendations:\n{recommendations}\n\nHospital Planning Actions:\n{hospital_plan}\n\nAlert Status: {'SMS Sent' if alert_needed else 'No Alert'}\nAlert Level: {alert_level.value.upper() if alert_needed else 'N/A'}\nReason: {reason}\n\n---\nFeedback: {feedback}\nComments: {comments}"
    st.download_button("Download Detailed Report", output_text, file_name="hospital_surge_agentic_report.txt")
