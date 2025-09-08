import streamlit as st
import openai
import pandas as pd
import re
from datetime import datetime
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="API key")

# Streamlit UI
st.title("🏥 Healthcare Appointment Finder")

# Sidebar filter for rating
st.sidebar.header("🔍 Filter Options")
min_rating = st.sidebar.selectbox("Minimum Doctor Rating", [0, 3, 4, 4.5, 5], index=0)

# Text input
report = st.text_area("📄 Paste the Patient's Diagnosis Report:", height=200, placeholder="Example: I've been experiencing eye pain. I live in Munich, zip 80331...")

if st.button("🔍 Analyze and Show Available Doctors") and report.strip():
    with st.spinner("Analyzing the report..."):
        try:
            # Step 1: GPT analysis
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": f"""
Analyze this patient report:\n{report}

Return your output in the format:
Specialist Needed: <type>
Severity Level: <1–10>
Location: <city>
ZIP Code: <zip>
"""}
                ]
            )

            reply = response.choices[0].message.content
            st.subheader("🧠 AI Diagnosis Summary")
            st.code(reply)

            # Parse GPT output
            specialty_match = re.search(r'Specialist Needed:\s*(.+)', reply, re.IGNORECASE)
            severity_match = re.search(r'Severity Level:\s*(\d+)', reply, re.IGNORECASE)
            location_match = re.search(r'Location:\s*(.+)', reply, re.IGNORECASE)
            zip_match = re.search(r'ZIP Code:\s*(\d+)', reply, re.IGNORECASE)

            specialty_needed = specialty_match.group(1).strip() if specialty_match else ""
            severity = int(severity_match.group(1)) if severity_match else 0
            location = location_match.group(1).strip() if location_match else ""
            zip_code = zip_match.group(1).strip() if zip_match else ""

            # Load and process doctor data
            df = pd.read_csv("doctor_database.csv")
            df["city"] = df["City/Zip"].apply(lambda x: x.split("/")[0].strip())
            df["zip"] = df["City/Zip"].apply(lambda x: x.split("/")[-1].strip())
            df["specialty"] = df["Specialist"]
            df["available_slot"] = df["Available Slot"]
            df["rating"] = df["Rating"]

            # Filter
            filtered_df = df[
                (df["specialty"].str.lower() == specialty_needed.lower()) &
                (
                    (df["city"].str.lower() == location.lower()) |
                    (df["zip"] == zip_code)
                ) &
                (df["rating"] >= min_rating)
            ]

            filtered_df = filtered_df.sort_values(by=["available_slot", "rating"], ascending=[True, False])

            st.subheader("✅ Matching Doctors")
            if filtered_df.empty:
                st.warning("No matching doctors found. Try adjusting the rating filter or updating the report.")
            else:
                st.success(f"Found {len(filtered_df)} doctors with rating ≥ {min_rating}⭐")
                st.dataframe(filtered_df[["Doctor Name", "specialty", "city", "zip", "available_slot", "rating"]].reset_index(drop=True))

            # Optional: Log interaction
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "patient_report": report,
                "specialist": specialty_needed,
                "severity": severity,
                "location": location,
                "zip": zip_code,
                "min_rating": min_rating,
                "matched_doctors": len(filtered_df)
            }
            log_df = pd.DataFrame([log_data])
            log_df.to_csv("interaction_log.csv", mode="a", header=not pd.io.common.file_exists("interaction_log.csv"), index=False)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

else:
    st.info("Enter a diagnosis report above and click the button to get started.")
