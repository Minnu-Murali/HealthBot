import streamlit as st
import pandas as pd

# Dummy GPT-style analyzer (replace with real GPT logic)
def analyze_report(report_text):
    return {
        "specialty": "Orthopedic",
        "severity": 8,
        "location": "Munich",
        "zip": "80331"
    }

@st.cache_data
def load_doctor_data():
    df = pd.read_csv("doctor_database.csv")
    df[['City', 'Zip']] = df['City/Zip'].str.split(" / ", expand=True)
    return df

st.set_page_config(page_title="Healthcare Appointment System123", layout="centered")
st.title("🏥 Healthcare Appointment Finder")

st.subheader("📄 Enter Patient Report")
report_text = st.text_area("Paste the patient's diagnosis report", height=200)

if report_text:
    st.subheader("🧠 AI Diagnosis Summary")
    result = analyze_report(report_text)

    st.markdown(f"**Specialist Needed:** `{result['specialty']}`")
    st.markdown(f"**Severity Level:** `{result['severity']}`")
    st.markdown(f"**Patient Location:** `{result['location']}`")
    st.markdown(f"**ZIP Code:** `{result['zip']}`")

    df = load_doctor_data()

    st.divider()
    st.subheader("⚙️ Filters and Preferences")

    # Filter: Minimum Rating
    min_rating = st.slider("Minimum Doctor Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)

    # Sort Priority
    sort_priority = st.radio("Sort doctors by", ["Earliest Slot", "Highest Rating"])

    # Match Preference
    location_preference = st.radio("Prefer match based on", ["City", "ZIP Code"])

    # Filtering logic
    if location_preference == "City":
        location_match = (df["City"].str.lower() == result["location"].lower())
    else:
        location_match = (df["Zip"] == result["zip"])

    filtered_doctors = df[
        (df["Specialist"].str.lower() == result["specialty"].lower()) &
        location_match &
        (df["Rating"] >= min_rating)
    ]

    if sort_priority == "Earliest Slot":
        filtered_doctors = filtered_doctors.sort_values(by=["Available Slot", "Rating"], ascending=[True, False])
    else:
        filtered_doctors = filtered_doctors.sort_values(by=["Rating", "Available Slot"], ascending=[False, True])

    st.divider()
    st.subheader("👨‍⚕️ Available Doctors")
    if not filtered_doctors.empty:
        st.dataframe(filtered_doctors[["Doctor Name", "Specialist", "City", "Zip", "Available Slot", "Rating"]])
    else:
        st.warning("❌ No matching doctors found with the selected filters.")
else:
    st.info("Paste a patient report above to begin.")
