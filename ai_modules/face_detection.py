"""
Face Detection Module
Uses OpenCV Haar Cascade and MediaPipe for advanced face detection.
"""
import cv2
import numpy as np
from typing import Tuple, List


def detect_faces(frame: np.ndarray) -> Tuple[int, List]:
    """
    Detect faces in a frame.
    Returns: (face_count, face_rectangles)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    count = len(faces) if hasattr(faces, '__len__') else 0
    return count, faces


def draw_face_boxes(frame: np.ndarray, faces) -> np.ndarray:
    """Draw bounding boxes around detected faces."""
    out = frame.copy()
    if hasattr(faces, '__iter__'):
        for (x, y, w, h) in faces:
            cv2.rectangle(out, (x, y), (x+w, y+h), (0, 212, 255), 2)
    return out
