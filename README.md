# IHRS — Interoperable Hospital Record Sharing System

**IHRS** is a web-based healthcare platform built to explore how hospitals can securely share patient records across independent systems — a real challenge in healthcare interoperability and value-based care coordination.

The system is designed around **patient privacy, consent, security, and accountability**, so that authorized healthcare professionals can only access records when they actually have the required permissions.

### ✨ Key Features

* 🚨 Emergency access mechanism with mandatory justification (break-glass access)
* 📋 Tamper-evident audit logs using hash chains
* 🩺 NEWS2-based clinical risk scoring
* 👥 Role-Based Access Control (RBAC) across patient, doctor, receptionist, and hospital-admin roles
* ✅ Patient consent management
* 🆔 Unique National Health ID (NHID) for patients
* 🏥 Secure cross-hospital health record sharing
* 🔐 Encrypted data storage and transfer (AES, RSA)
* 🌱 Lifestyle recommendations based on patient data
* 🔗 Peer-hospital communication

### 🛠️ Tech Stack

**Backend:** Django, Django REST Framework, PostgreSQL
**Frontend:** React, Vite, Tailwind CSS, Axios
**Security:** AES-128, RSA, RBAC, SHA-256 hash chain

### 🏗️ How it works

Each hospital runs its own independent database on its own server — one on PostgreSQL, one on MySQL — and the two servers talk to each other over authenticated REST API calls when a record needs to be shared. When a doctor at Hospital A requests a patient's record from Hospital B, the request goes through the RBAC and consent layer first — if the patient hasn't consented and it isn't an emergency, the request gets denied. Emergency (break-glass) access bypasses this but requires a written justification and gets logged in the tamper-evident audit trail.

### 📂 Project Structure

IHRS/
├── ihrs-backend/      # Django REST API
└── ihrs-frontend/     # React frontend


### 🚀 Getting Started

**Backend**
cd ihrs-backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


**Frontend**
cd ihrs-frontend
npm install
npm run dev


### 👩‍💻 Team

**Mitrata Bhandari** — Backend Development
**Aakriti Simkhada** — Frontend Development

IHRS is an academic project developed to explore secure and interoperable healthcare record sharing. It is not intended for handling real patient data in its current form.