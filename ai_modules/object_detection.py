"""
Object Detection Module
Optional: Uses YOLOv8 (ultralytics) to detect prohibited objects.
Falls back gracefully if not installed.
"""
from typing import List, Dict


PROHIBITED_CLASSES = {
    'cell phone':     ('phone_detected',     25),
    'book':           ('book_detected',      10),
    'laptop':         ('suspicious_object',  15),
    'tablet':         ('suspicious_object',  15),
    'remote':         ('suspicious_object',   5),
    'keyboard':       ('suspicious_object',   5),
    'mouse':          ('suspicious_object',   5),
    'person':         None,  # handled by face detection
}


def detect_objects(frame) -> List[Dict]:
    """
    Run YOLOv8 object detection on a frame.
    Returns list of detected prohibited objects with event and penalty.
    """
    detections = []

    try:
        from ultralytics import YOLO
        import numpy as np

        model = YOLO('yolov8n.pt')  # nano model for speed
        results = model(frame, verbose=False)

        for result in results:
            for box in result.boxes:
                cls_name = result.names[int(box.cls[0])].lower()
                conf = float(box.conf[0])

                if conf < 0.5:
                    continue

                if cls_name in PROHIBITED_CLASSES and PROHIBITED_CLASSES[cls_name]:
                    event_type, penalty = PROHIBITED_CLASSES[cls_name]
                    detections.append({
                        'class': cls_name,
                        'confidence': round(conf, 2),
                        'event_type': event_type,
                        'penalty': penalty,
                        'bbox': box.xyxy[0].tolist()
                    })

    except ImportError:
        pass  # YOLOv8 not installed — feature disabled
    except Exception as e:
        print(f"Object detection error: {e}")

    return detections
