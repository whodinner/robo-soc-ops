# app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio

from . import db
from .models import Event
from .triage import AITriage

app = FastAPI()
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

triage_engine = AITriage()

class IncidentLogger:
    def __init__(self):
        self.connections = []

    async def broadcast(self, event_dict):
        for connection in self.connections:
            try:
                await connection.send_json(event_dict)
            except Exception:
                pass

    def log(self, event: Event):
        # Run AI triage
        triage_engine.analyze(event)

        data = event.dict()

        # Store in DB
        with db.db_cursor() as cursor:
            cursor.execute("""INSERT INTO incidents 
                (id, timestamp, type, source, details, severity, handled_by, latitude, longitude, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["id"], data["timestamp"], data["type"], data["source"], data["details"],
                    data["severity"], data.get("handled_by"), data.get("latitude"), data.get("longitude"), "OPEN"
                )
            )

        # Notify dashboard clients
        asyncio.create_task(self.broadcast(data))
        return data

incident_logger = IncidentLogger()


@app.get("/")
def home():
    return {"message": "RoboSOC running. Open /dashboard for UI."}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    with open("templates/dashboard.html") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/incidents")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    incident_logger.connections.append(ws)
    try:
        while True:
            await ws.receive_text()  # keeps connection alive
    except WebSocketDisconnect:
        incident_logger.connections.remove(ws)


@app.get("/incidents")
def get_incidents():
    with db.db_cursor() as cursor:
        cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
    return [dict(r) for r in rows]


@app.post("/incidents/new")
def new_incident(event_type: str = Body(...), source: str = Body(...), details: str = Body(...)):
    event = Event(type=event_type, source=source, details=details)
    return incident_logger.log(event)
