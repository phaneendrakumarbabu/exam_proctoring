"""
Gaze Tracking Module
Uses MediaPipe FaceMesh to estimate gaze direction and head orientation.
"""
import numpy as np
from typing import Dict, Optional


def analyze_gaze(frame: np.ndarray) -> Dict:
    """
    Analyze gaze and head orientation from a video frame.
    Returns dict with: looking_away, head_turned, pitch, yaw, roll
    """
    result = {
        'looking_away': False,
        'head_turned': False,
        'pitch': 0.0,
        'yaw': 0.0,
        'roll': 0.0
    }

    try:
        import mediapipe as mp
        import cv2

        mp_face_mesh = mp.solutions.face_mesh
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return result

            landmarks = results.multi_face_landmarks[0].landmark
            h, w = frame.shape[:2]

            # Key landmarks
            nose      = landmarks[1]
            l_eye_in  = landmarks[133]
            r_eye_in  = landmarks[362]
            chin      = landmarks[152]
            forehead  = landmarks[10]

            # Yaw (left-right turn)
            nose_x    = nose.x * w
            center_x  = w / 2
            yaw       = (nose_x - center_x) / (w / 2)

            # Pitch (up-down tilt)
            eye_y     = ((l_eye_in.y + r_eye_in.y) / 2) * h
            nose_y    = nose.y * h
            pitch     = (nose_y - eye_y) / (h * 0.15)

            result['yaw']   = round(yaw, 3)
            result['pitch'] = round(pitch, 3)

            if abs(yaw) > 0.25:
                result['head_turned']  = True
            if abs(pitch) > 0.35 or abs(nose.z) > 0.15:
                result['looking_away'] = True

    except ImportError:
        pass  # MediaPipe not installed — skip
    except Exception:
        pass

    return result


def is_gaze_on_screen(gaze_result: Dict, threshold: float = 0.3) -> bool:
    """Returns True if the student appears to be looking at the screen."""
    return (
        not gaze_result.get('looking_away', False) and
        not gaze_result.get('head_turned', False) and
        abs(gaze_result.get('yaw', 0)) < threshold
    )
