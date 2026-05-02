import re
from fastapi import Response
from fastapi.responses import Response
from fastapi import Form
from twilio.twiml.messaging_response import MessagingResponse
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI(title="DjibCare AI Appointment Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./appointments.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    phone = Column(String)
    preferred_date = Column(String)
    preferred_time = Column(String)
    reason = Column(String)

Base.metadata.create_all(bind=engine)

class PatientMessage(BaseModel):
    message: str

class AppointmentRequest(BaseModel):
    full_name: str
    phone: str
    preferred_date: str
    preferred_time: str
    reason: str

@app.get("/")
def home():
    return {"message": "DjibCare AI Appointment Agent is running."}

@app.post("/chat")
def chat(patient: PatientMessage):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "full_name": "",
            "phone": "",
            "preferred_date": "",
            "preferred_time": "",
            "reason": "",
            "message": "Hello, I’m DjibCare AI. Please send your full name, phone number, preferred date, preferred time, and reason for visit."
        }

    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are DjibCare AI, a clinic appointment assistant.

                    Extract appointment details from the patient message.

                    Return ONLY valid JSON in this exact format:
                    {
                      "full_name": "",
                      "phone": "",
                      "preferred_date": "",
                      "preferred_time": "",
                      "reason": "",
                      "message": ""
                    }

                    If information is missing, leave the field empty and ask for it in message.
                    Do not give medical diagnosis.
                    """
                },
                {
                    "role": "user",
                    "content": patient.message
                }
            ]
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        return {
            "full_name": "",
            "phone": "",
            "preferred_date": "",
            "preferred_time": "",
            "reason": "",
            "message": f"AI service issue: {str(e)}"
        }

@app.post("/book-appointment")
def book_appointment(appointment: AppointmentRequest):
    db = SessionLocal()

    new_appointment = Appointment(
        full_name=appointment.full_name,
        phone=appointment.phone,
        preferred_date=appointment.preferred_date,
        preferred_time=appointment.preferred_time,
        reason=appointment.reason
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    db.close()

    return {
        "message": "Appointment saved successfully.",
        "appointment_id": new_appointment.id,
        "patient": appointment.full_name
    }

@app.get("/appointments")
def get_appointments():
    db = SessionLocal()
    appointments = db.query(Appointment).all()
    db.close()
    return appointments

@app.post("/whatsapp")
def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    incoming_message = Body.strip()
    twilio_response = MessagingResponse()

    # Simple extractor for first working WhatsApp demo
    name_match = re.search(r"my name is ([a-zA-Z\s]+)", incoming_message, re.IGNORECASE)
    phone_match = re.search(r"(\d{9,15})", incoming_message)
    date_match = re.search(r"(may\s+\d+|tomorrow|today|\d{4}-\d{2}-\d{2})", incoming_message, re.IGNORECASE)
    time_match = re.search(r"(\d{1,2}\s?(am|pm)|\d{1,2}:\d{2})", incoming_message, re.IGNORECASE)

    full_name = name_match.group(1).strip() if name_match else ""
    phone = phone_match.group(1).strip() if phone_match else From.replace("whatsapp:", "")
    preferred_date = date_match.group(1).strip() if date_match else ""
    preferred_time = time_match.group(1).strip() if time_match else ""

    reason = "General consultation"
    if "checkup" in incoming_message.lower():
        reason = "Checkup"
    elif "consultation" in incoming_message.lower():
        reason = "Consultation"
    elif "pain" in incoming_message.lower():
        reason = "Pain / Medical concern"

    if full_name and phone and preferred_date and preferred_time:
        db = SessionLocal()

        new_appointment = Appointment(
            full_name=full_name,
            phone=phone,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            reason=reason
        )

        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        db.close()

        twilio_response.message(
            f"✅ Appointment booked successfully!\n\n"
            f"Patient: {full_name}\n"
            f"Date: {preferred_date}\n"
            f"Time: {preferred_time}\n"
            f"Reason: {reason}\n"
            f"Booking ID: {new_appointment.id}"
        )

    else:
        twilio_response.message(
            "Welcome to DjibCare AI.\n\n"
            "Please send your appointment request like this:\n\n"
            "My name is Moustapha Ilmi, phone 7018640231, I want an appointment on May 5 at 10 AM for checkup"
        )

    return Response(content=str(twilio_response), media_type="application/xml")
