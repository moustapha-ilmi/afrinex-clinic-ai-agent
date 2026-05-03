# 🚀 DjibCare AI — WhatsApp Appointment Booking Agent

> A production-ready AI system that automates clinic appointment booking through WhatsApp using natural language.

## 🌍 Overview

**DjibCare AI** is an AI-powered assistant that enables clinics to automate patient scheduling through simple WhatsApp conversations.

Instead of calling or filling out forms, patients can send a message like:

I want to book an appointment tomorrow at 10am

The system will:
- understand the request
- extract key details (name, phone, date, time, reason)
- save the appointment in a database
- send an instant confirmation

👉 No apps. No forms. Just conversation.

---

## ⚡ Key Features

- 🤖 **AI-powered conversation engine**
- 💬 **WhatsApp integration (Twilio API)**
- 📅 **Automatic appointment booking**
- 🧠 **Structured data extraction from natural language**
- 📊 **Admin dashboard for clinic staff**
- 🌐 **Live deployment (Render)**
- 💻 **Clean frontend interface for demo/testing**

---

## 🏗️ System Architecture
Patient (WhatsApp)
↓
Twilio Webhook
↓
FastAPI Backend (AI + Business Logic)
↓
SQLite Database
↓
Admin Dashboard (Web Interface)

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **AI Layer:** OpenAI API
- **Database:** SQLite (SQLAlchemy ORM)
- **Messaging:** Twilio WhatsApp API
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render


## 🔄 End-to-End Flow

1. Patient sends a WhatsApp message  
2. AI processes and extracts appointment details  
3. Missing info is requested automatically  
4. Appointment is saved in the database  
5. Confirmation is sent instantly  

Example confirmation:

✅ Appointment Confirmed
👤 Name: Moustapha Ilmi
📅 Date: May 5
⏰ Time: 10 AM
🩺 Reason: Checkup
🆔 Booking ID: 12


## 💡 Real-World Impact

Healthcare providers often struggle with:
- high call volume
- manual scheduling errors
- limited availability outside working hours

**DjibCare AI solves this by enabling 24/7 automated booking**, improving both:
- patient experience
- clinic operational efficiency


## 📈 Business & Product Vision

This project is designed as a scalable SaaS solution:

- Subscription model for clinics ($50–$200/month)
- Deployment across clinics, hospitals, and NGOs
- Strong fit for regions where WhatsApp is the primary communication tool


## 🔮 Future Enhancements

- 🌐 Multi-language support (French / Arabic / English)
- 🔐 Authentication & role-based dashboards
- 📩 Automated reminders & notifications
- 🏥 Multi-clinic management system
- 💳 Payment & billing integration

## 👨‍💻 Author

**Moustapha Ilmi**  
AI Engineer | Cloud & DevOps  
Founder @ Afrinex AI  

