import streamlit as st
import json
import os
from agent import process_enquiry

st.set_page_config(
    page_title="WhatsApp Enquiry Handler",
    page_icon="🏥",
    layout="centered"
)

st.title("🏥 WhatsApp Enquiry Handler")
st.markdown("**Al-Shifa Diagnostic Center** — AI Patient Support Agent")
st.divider()

st.subheader("📩 Simulate Patient Message")
patient_message = st.text_area(
    "Enter patient WhatsApp message:",
    placeholder="e.g. Hi, I want to book an appointment for a blood test...",
    height=120
)

submit = st.button("🚀 Process Message", use_container_width=True)

if submit:
    if not patient_message.strip():
        st.warning("Please enter a patient message first.")
    else:
        with st.spinner("Processing..."):
            try:
                result = process_enquiry(patient_message)

                st.divider()
                st.subheader("📊 Result")

                if result["human_handoff"]:
                    st.error("🚨 HUMAN HANDOFF TRIGGERED — Flagged for staff review!")
                else:
                    st.success(f"✅ Category: **{result['category']}**")

                st.subheader("💬 AI Response")
                st.info(result["response"])

                with st.expander("📋 Log Entry"):
                    st.json({
                        "timestamp": result["timestamp"],
                        "category": result["category"],
                        "human_handoff": result["human_handoff"],
                        "patient_message": patient_message,
                        "ai_response": result["response"]
                    })

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.subheader("📁 Enquiry Log History")

LOG_FILE = "enquiry_log.json"

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        try:
            logs = json.load(f)
            if logs:
                for log in reversed(logs):
                    icon = "🚨" if log.get("human_handoff") else "✅"
                    with st.expander(f"{icon} [{log['timestamp']}] — {log['category']}"):
                        st.markdown(f"**Patient:** {log['patient_message']}")
                        st.markdown(f"**AI Response:** {log['ai_response']}")
                        st.markdown(f"**Human Handoff:** {'Yes ⚠️' if log.get('human_handoff') else 'No'}")
            else:
                st.info("No enquiries logged yet.")
        except:
            st.info("No enquiries logged yet.")
else:
    st.info("No enquiries logged yet. Submit a message above!")

st.divider()
st.caption("Built with Python + Google Gemini AI | Synops Labs Technical Assessment")
