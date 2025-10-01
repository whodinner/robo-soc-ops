# app/models.py
import uuid, datetime as dt
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator


# --- Event Model ---
class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: dt.datetime.utcnow().isoformat())
    type: str
    source: str
    details: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW"
    handled_by: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ai_triage: Optional[str] = None

    @validator("details")
    def details_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Event details cannot be empty")
        return v


# --- Audit Trail ---
class IncidentAudit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str
    timestamp: str = Field(default_factory=lambda: dt.datetime.utcnow().isoformat())
    action: str
    details: Optional[str] = None
    operator: str
    hash: Optional[str] = None  # for tamper-proofing


# --- Shift Handovers ---
class ShiftHandover(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: dt.datetime.utcnow().isoformat())
    operator: str
    notes: str


# --- User Model ---
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    role: Literal["admin", "operator", "viewer"] = "operator"
