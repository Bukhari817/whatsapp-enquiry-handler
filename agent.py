import google.generativeai as genai
import json
import os
from datetime import datetime

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found! Add it in Replit Secrets.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

LOG_FILE = "enquiry_log.json"

CATEGORIES = [
    "Appointment Booking",
    "Service / Pricing Question",
    "Report Status Follow-up",
    "Home Healthcare Request",
    "Other"
]

HUMAN_HANDOFF_KEYWORDS = [
    "urgent", "complaint", "speak to someone",
    "manager", "emergency", "complain"
]


def check_human_handoff(message: str) -> bool:
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in HUMAN_HANDOFF_KEYWORDS)


def classify_enquiry(message: str) -> str:
    prompt = f"""You are a classifier for a diagnostic center's WhatsApp enquiries.

Classify the following patient message into EXACTLY ONE of these categories:
1. Appointment Booking
2. Service / Pricing Question
3. Report Status Follow-up
4. Home Healthcare Request
5. Other

Patient message: "{message}"

Reply with ONLY the category name, nothing else."""

    response = model.generate_content(prompt)
    category = response.text.strip()

    for cat in CATEGORIES:
        if cat.lower() in category.lower():
            return cat
    return "Other"


def generate_response(message: str, category: str) -> str:
    category_prompts = {
        "Appointment Booking": "Help the patient book an appointment. Ask for preferred date, time, and type of test needed.",
        "Service / Pricing Question": "Provide helpful information about services and pricing. Guide them to the right service.",
        "Report Status Follow-up": "Help the patient check their report status. Ask for their patient ID or name and date of test.",
        "Home Healthcare Request": "Assist with home healthcare request. Ask for location, service type, and preferred timing.",
        "Other": "Provide a warm, helpful response and guide them to the right department."
    }

    prompt = f"""You are a professional and warm customer service agent for Al-Shifa Diagnostic Center.

Patient message: "{message}"
Category: {category}
Your task: {category_prompts.get(category, category_prompts["Other"])}

Guidelines:
- Be professional, warm, and concise
- Keep response under 100 words
- End with a helpful next step
- Do NOT use markdown formatting
- Write in a conversational, caring tone"""

    response = model.generate_content(prompt)
    return response.text.strip()


def log_enquiry(message: str, category: str, response: str, is_handoff: bool):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient_message": message,
        "category": category,
        "ai_response": response,
        "human_handoff": is_handoff
    }

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    return log_entry


def process_enquiry(message: str) -> dict:
    is_handoff = check_human_handoff(message)

    if is_handoff:
        category = "Human Handoff Required"
        response = "This enquiry has been flagged for human review. A staff member will contact you shortly. Thank you for your patience."
    else:
        category = classify_enquiry(message)
        response = generate_response(message, category)

    log_entry = log_enquiry(message, category, response, is_handoff)

    return {
        "category": category,
        "response": response,
        "human_handoff": is_handoff,
        "timestamp": log_entry["timestamp"]
    }
