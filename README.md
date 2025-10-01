# RoboSOC - Robotic Security Operations Center 

This project simulates the role of a Security Operations Center (SOC) Operator using robotics, AI, and automation.
CCTV Monitoring (YOLOv8)

Person detection with restricted zone alerts

Real-time video streaming with bounding boxes

Incident Management

Logging, triage, severity levels (LOW → CRITICAL)

AI-assisted decision-making (rules + optional NLP/ML)

Communication Integration

Twilio call intake (stubbed)

Tulip survey pipeline (configurable)

Automated Dispatch

MQTT integration for drones, robots, guards

Configurable unit-specific payloads (altitude, patrol speed, radio contact)

Real-Time Dashboard (FastAPI + WebSockets)

Live incident feed

CCTV stream

Interactive map (Leaflet.js)

Analytics (Chart.js)

Snapshots per incident

Audit trail & timeline

Shift handover log

Authentication & Roles

Operator, Supervisor, Admin

JWT-based auth with bcrypt password hashing

# Dashboard Preview
Live incident list with severity coloring

Leaflet map plotting incident locations

Charts for incident trends & severity distribution

Live CCTV feed (stubbed, ready for integration)

# Security Notes
Passwords hashed with bcrypt (passlib)

JWT tokens (HS256) with short expiration

SQLite with context-managed writes and audit logs

MQTT secured with TLS

## Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open http://localhost:8000/dashboard
