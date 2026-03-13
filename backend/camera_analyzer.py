import numpy as np
import cv2
import base64
from typing import Dict, List
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class CameraAnalyzer:
    def __init__(self):
        self.face_cascade = None
        self.eye_cascade = None
        self.mp_face_mesh = None
        self._init_detectors()

    def _init_detectors(self):
        """Initialize face and eye cascades for robust detection"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                print("[WARN] Face cascade failed to load")
                self.face_cascade = None
            else:
                print("[OK] Face cascade loaded")
        except Exception as e:
            print(f"Face cascade init error: {e}")
            self.face_cascade = None

        try:
            eye_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            self.eye_cascade = cv2.CascadeClassifier(eye_path)
            if self.eye_cascade.empty():
                self.eye_cascade = None
        except Exception:
            self.eye_cascade = None

        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=4,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            print("[OK] MediaPipe loaded")
        except Exception as e:
            print(f"MediaPipe init error: {e}")
            self.mp_face_mesh = None

    def analyze(self, frame_bytes: bytes) -> Dict:
        events: List[str] = []
        analysis = {
            'faces': 0,
            'looking_away': False,
            'head_turned': False,
            'suspicious': False,
            'events': events
        }

        # Decode image
        try:
            arr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                return analysis
        except Exception as e:
            print(f"Frame decode error: {e}")
            return analysis

        try:
            # Preprocess image for better detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast for better face detection
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
            
        except Exception as e:
            print(f"Color conversion error: {e}")
            return analysis

        # Face detection
        face_count = self._detect_faces(gray, img)
        analysis['faces'] = face_count

        # Only flag "no_face" if we're very confident there's no face
        if face_count == 0:
            events.append('no_face')
        elif face_count > 1:
            events.append('multiple_faces')

        # Head pose / gaze via MediaPipe (only if we detected exactly 1 face)
        if face_count == 1 and self.mp_face_mesh:
            pose = self._analyze_head_pose(img)
            if pose.get('head_turned'):
                events.append('head_turned')
                analysis['head_turned'] = True
            if pose.get('looking_away'):
                events.append('looking_away')
                analysis['looking_away'] = True

        analysis['suspicious'] = len(events) > 0
        return analysis

    def _detect_faces(self, gray_img, color_img=None) -> int:
        """Detect faces using multiple cascade classifiers for high accuracy"""
        if self.face_cascade is None or self.face_cascade.empty():
            return 0  # No detector available

        try:
            all_faces = []
            
            # Method 1: Frontal face detection (primary)
            faces_frontal = self.face_cascade.detectMultiScale(
                gray_img, 
                scaleFactor=1.08,
                minNeighbors=6,
                minSize=(40, 40),
                maxSize=(400, 400),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            if isinstance(faces_frontal, np.ndarray) and len(faces_frontal) > 0:
                all_faces.extend(faces_frontal)
            
            # Method 2: Try alternative cascade if available
            if self.eye_cascade and not self.eye_cascade.empty():
                try:
                    eyes = self.eye_cascade.detectMultiScale(
                        gray_img,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(15, 15)
                    )
                    # If we detect eyes, we likely have a face
                    if isinstance(eyes, np.ndarray) and len(eyes) >= 2:
                        # Eyes detected = face present
                        if len(all_faces) == 0:
                            all_faces.append([0, 0, gray_img.shape[1], gray_img.shape[0]])
                except Exception:
                    pass
            
            # Remove duplicate detections (overlapping boxes)
            if len(all_faces) > 0:
                all_faces = self._remove_duplicate_faces(all_faces)
                return len(all_faces)
            
            return 0
        except Exception as e:
            print(f"Face detection error: {e}")
            return 0
    
    def _remove_duplicate_faces(self, faces):
        """Remove overlapping face detections"""
        if len(faces) <= 1:
            return faces
        
        # Sort by area (largest first)
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        unique_faces = []
        
        for face in faces:
            x1, y1, w1, h1 = face
            is_duplicate = False
            
            for ux, uy, uw, uh in unique_faces:
                # Calculate overlap
                overlap_x = max(0, min(x1+w1, ux+uw) - max(x1, ux))
                overlap_y = max(0, min(y1+h1, uy+uh) - max(y1, uy))
                overlap_area = overlap_x * overlap_y
                
                # If overlap > 30%, consider it duplicate
                if overlap_area > (w1*h1*0.3):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_faces.append(face)
        
        return unique_faces

    def _analyze_head_pose(self, img) -> Dict:
        result = {'head_turned': False, 'looking_away': False}
        try:
            if self.mp_face_mesh is None:
                return result
                
            import mediapipe as mp
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.mp_face_mesh.process(rgb)

            if not results.multi_face_landmarks or len(results.multi_face_landmarks) == 0:
                return result

            landmarks = results.multi_face_landmarks[0].landmark
            h, w = img.shape[:2]

            # Key facial landmarks for head pose estimation
            nose = landmarks[1]           # Nose tip
            left_eye = landmarks[33]      # Left eye outer corner
            right_eye = landmarks[263]    # Right eye outer corner
            left_mouth = landmarks[61]    # Left mouth corner
            right_mouth = landmarks[291]  # Right mouth corner
            chin = landmarks[152]         # Chin

            # Calculate head position
            nose_x = nose.x * w
            center_x = w / 2
            
            # Head turn detection (horizontal deviation)
            deviation = abs(nose_x - center_x) / (w / 2)
            if deviation > 0.3:  # More than 30% deviation
                result['head_turned'] = True
            
            # Looking away detection (vertical and depth)
            nose_y = nose.y * h
            center_y = h / 2
            vertical_deviation = abs(nose_y - center_y) / (h / 2)
            
            # If nose is significantly below center or z-depth is high
            if vertical_deviation > 0.35 or abs(nose.z) > 0.2:
                result['looking_away'] = True

        except Exception as e:
            print(f"Head pose analysis error: {e}")
        return result
