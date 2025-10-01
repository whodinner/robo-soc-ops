# app/cctv.py
import os
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict

# Load YOLOv8 model (configurable path, safer than hardcoding)
MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load YOLO model from {MODEL_PATH}: {e}")

# Configurable restricted zones
# Each zone is a polygon: list of (x, y) points
RESTRICTED_ZONES: List[List[Tuple[int, int]]] = [
    [(100, 100), (300, 100), (300, 300), (100, 300)]
]

# Minimum confidence threshold to reduce false positives
CONF_THRESHOLD = float(os.getenv("YOLO_CONF_THRESHOLD", 0.4))


def point_in_polygon(point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
    """Ray casting algorithm to test if point is inside polygon"""
    x, y = point
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def analyze_frame(frame: np.ndarray) -> Tuple[List[Dict], np.ndarray]:
    """
    Run YOLOv8 person detection + restricted zone violation check.

    Returns:
        detections (list): structured list of detected persons with bbox, confidence, and violation flag
        frame (ndarray): annotated frame with boxes and zones drawn
    """
    detections: List[Dict] = []
    try:
        results = model(frame)
    except Exception as e:
        raise RuntimeError(f"YOLO inference failed: {e}")

    for r in results:
        if not hasattr(r, "boxes"):
            continue
        boxes = r.boxes.xyxy.cpu().numpy()  # [x1,y1,x2,y2]
        confs = r.boxes.conf.cpu().numpy()
        clss = r.boxes.cls.cpu().numpy()

        for box, conf, cls in zip(boxes, confs, clss):
            if int(cls) == 0 and conf >= CONF_THRESHOLD:  # person class
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                violation = any(point_in_polygon((cx, cy), zone) for zone in RESTRICTED_ZONES)

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(float(conf), 3),
                    "restricted_violation": violation
                })

                # Visualization
                color = (0, 0, 255) if violation else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame, f"Person {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                )

    # Draw restricted zones clearly
    for zone in RESTRICTED_ZONES:
        cv2.polylines(frame, [np.array(zone, np.int32)], True, (255, 0, 0), 2)

    return detections, frame
