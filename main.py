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
    response = MessagingResponse()
    response.message("Hello from DjibCare AI. I received your WhatsApp message.")
    return Response(content=str(response), media_type="application/xml")

    if "appointment" in msg or "book" in msg:
        response.message(
            "Welcome to DjibCare AI. Please send your full name, preferred date, preferred time, and reason for visit."
        )
    elif "hours" in msg or "open" in msg:
        response.message("The clinic is open Monday to Saturday from 8:00 AM to 6:00 PM.")
    else:
        response.message(
            "Hello, I’m DjibCare AI. I can help you book a clinic appointment. Type: I want to book an appointment."
        )

    return str(response)
