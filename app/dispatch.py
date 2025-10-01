# app/dispatch.py
import os, json, ssl, uuid, datetime
import paho.mqtt.client as mqtt
from typing import Dict, Any

# MQTT config (TLS + env vars for safety)
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))  # 8883 = TLS
MQTT_TOPIC_BASE = os.getenv("MQTT_TOPIC_BASE", "robosoc/dispatch")
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

client = mqtt.Client(client_id=f"robosoc-dispatch-{uuid.uuid4()}")
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.tls_insecure_set(False)
if MQTT_USER and MQTT_PASS:
    client.username_pw_set(MQTT_USER, MQTT_PASS)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
except Exception as e:
    raise RuntimeError(f"Failed to connect to MQTT broker {MQTT_BROKER}:{MQTT_PORT} → {e}")


def dispatch_unit(unit_type: str, location: Dict[str, Any], severity: str = "LOW") -> Dict[str, Any]:
    """
    Securely dispatch a unit (drone, robot, guard) via MQTT.

    Args:
        unit_type (str): "drone", "robot", "guard"
        location (dict): {"lat": float, "lon": float}
        severity (str): severity level

    Returns:
        dict: Dispatch confirmation
    """
    if unit_type not in {"drone", "robot", "guard"}:
        raise ValueError(f"Unsupported unit_type '{unit_type}'")

    if not isinstance(location, dict) or "lat" not in location or "lon" not in location:
        raise ValueError("Invalid location format. Must include 'lat' and 'lon'.")

    payload = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "unit_type": unit_type,
        "location": location,
        "severity": severity
    }

    # Customize payload by type
    if unit_type == "drone":
        payload["action"] = "aerial_survey"
        payload["altitude"] = 50  # meters
    elif unit_type == "robot":
        payload["action"] = "ground_patrol"
        payload["speed"] = 1.5  # m/s
    elif unit_type == "guard":
        payload["action"] = "human_dispatch"
        payload["contact_channel"] = "radio"

    try:
        topic = f"{MQTT_TOPIC_BASE}/{unit_type}"
        client.publish(topic, json.dumps(payload), qos=1, retain=False)
        print(f"[DISPATCH] {unit_type.upper()} dispatched → {location} (severity={severity})")
    except Exception as e:
        raise RuntimeError(f"Failed to dispatch {unit_type}: {e}")

    return {"status": "dispatched", "topic": topic, "payload": payload}
