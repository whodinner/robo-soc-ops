# app/triage.py
import datetime as dt
from typing import Dict, Any
from app.models import Event


class AITriage:
    """
    AI-driven triage engine for SOC incidents.
    - Uses rules for high-confidence cases (fire, intrusion, etc.)
    - Falls back to NLP/ML model if available (plug-in ready)
    - Provides structured rationale for audit trail
    """

    def __init__(self, nlp_model=None):
        """
        Args:
            nlp_model: Optional ML/NLP classifier for threat categorization
        """
        self.nlp_model = nlp_model

    def analyze(self, event: Event) -> Dict[str, Any]:
        text = event.details.lower()
        now = dt.datetime.utcnow().isoformat()

        # --- Rule-based triage ---
        if "fire" in text or "smoke" in text:
            recommendation = {
                "suggested_severity": "CRITICAL",
                "action": "Dispatch Fire Team",
                "rationale": "Fire/smoke keyword detected",
                "confidence": 0.95,
                "analyzed_at": now,
            }

        elif any(word in text for word in ["unauthorized", "intrusion", "trespass"]):
            recommendation = {
                "suggested_severity": "HIGH",
                "action": "Dispatch Guard",
                "rationale": "Intrusion-related keyword detected",
                "confidence": 0.9,
                "analyzed_at": now,
            }

        elif "medical" in text or "injury" in text:
            recommendation = {
                "suggested_severity": "HIGH",
                "action": "Dispatch Medical Team",
                "rationale": "Medical emergency keyword detected",
                "confidence": 0.9,
                "analyzed_at": now,
            }

        else:
            # --- Optional NLP/ML fallback ---
            if self.nlp_model:
                predicted = self.nlp_model.predict(text)
                recommendation = {
                    "suggested_severity": predicted.get("severity", "LOW"),
                    "action": predicted.get("action", "Monitor"),
                    "rationale": f"ML model classification → {predicted.get('label')}",
                    "confidence": predicted.get("confidence", 0.7),
                    "analyzed_at": now,
                }
            else:
                recommendation = {
                    "suggested_severity": "LOW",
                    "action": "Monitor",
                    "rationale": "No high-risk keywords detected",
                    "confidence": 0.6,
                    "analyzed_at": now,
                }

        # Attach recommendation to event for persistence
        event.ai_triage = recommendation
        return recommendation
