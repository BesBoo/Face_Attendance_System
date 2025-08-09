# face_recognition_modules/mediapipe_recognizer.py

import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple, Optional
import os
from PIL import Image

class MediaPipeFaceRecognition:
    """
    MediaPipe-based face recognition class that replaces face_recognition library
    Provides similar interface but uses MediaPipe for face detection and custom encoding
    """
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=10,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        print(" MediaPipe Face Recognition initialized")
    
    def load_image_file(self, image_path: str) -> np.ndarray:
        """
        Load an image file and return as RGB numpy array
        Compatible with face_recognition.load_image_file()
        """
        try:
            
            with Image.open(image_path) as pil_image:
                
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                
                image = np.array(pil_image)
                
                print(f"Successfully ! Loaded image: {image_path}, shape: {image.shape}")
                return image
                
        except Exception as e:
            print(f"❌ Error loading image {image_path}: {e}")
            try:
                image = cv2.imread(image_path)
                if image is not None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    return image
                else:
                    raise ValueError(f"Could not load image: {image_path}")
            except Exception as cv_error:
                raise ValueError(f"Failed to load image with both PIL and OpenCV: {cv_error}")
    
    def face_locations(self, image: np.ndarray, model: str = "hog") -> List[Tuple[int, int, int, int]]:
        """
        Find face locations in image
        Returns list of tuples (top, right, bottom, left) - compatible with face_recognition
        """
        try:
            if len(image.shape) == 3 and image.shape[2] == 3:
                mp_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                mp_image = image
            
            results = self.face_detection.process(mp_image)
            
            locations = []
            if results.detections:
                height, width = image.shape[:2]
                
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    
                    left = int(bbox.xmin * width)
                    top = int(bbox.ymin * height)
                    right = int((bbox.xmin + bbox.width) * width)
                    bottom = int((bbox.ymin + bbox.height) * height)
                    
                    
                    left = max(0, left)
                    top = max(0, top)
                    right = min(width, right)
                    bottom = min(height, bottom)
                    
                   
                    locations.append((top, right, bottom, left))
            
            return locations
            
        except Exception as e:
            print(f"❌ Face location detection error: {e}")
            return []
    
    def face_encodings(self, image: np.ndarray, known_face_locations: Optional[List] = None, num_jitters: int = 1, model: str = "small") -> List[np.ndarray]:
        """
        Generate face encodings for faces in image
        Returns list of 128-dimensional face encodings
        """
        try:
            if known_face_locations is None:
                known_face_locations = self.face_locations(image)
            
            if not known_face_locations:
                return []
            
            encodings = []
            
            if len(image.shape) == 3 and image.shape[2] == 3:
                mp_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                mp_image = image
            
            mesh_results = self.face_mesh.process(mp_image)
            
            if mesh_results.multi_face_landmarks:
                height, width = image.shape[:2]
                
                for i, face_landmarks in enumerate(mesh_results.multi_face_landmarks):
                    if i < len(known_face_locations):
                        encoding = self._extract_face_encoding(face_landmarks, width, height)
                        encodings.append(encoding)
            else:
                for location in known_face_locations:
                    top, right, bottom, left = location
                    face_region = image[top:bottom, left:right]
                    encoding = self._create_basic_encoding(face_region)
                    encodings.append(encoding)
            
            return encodings
            
        except Exception as e:
            print(f"❌ Face encoding error: {e}")
            return []
    
    def _extract_face_encoding(self, landmarks, width: int, height: int) -> np.ndarray:
        """
        Extract face encoding from MediaPipe face landmarks
        Creates a 128-dimensional feature vector
        """
        try:

            key_points = [
                # Nose tip, nose bridge
                1, 2, 5, 4, 6, 19, 20, 94, 125, 141, 235, 236, 3, 51, 48, 115, 131, 134, 102, 49, 220, 305, 307, 375, 321, 308, 324, 318,
                # Eyes
                33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382,
                # Eyebrows  
                70, 63, 105, 66, 107, 55, 65, 52, 53, 46, 285, 295, 282, 283, 276, 300, 293, 334, 296, 336,
                # Mouth
                61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318
            ]
            
            features = []
            for point_idx in key_points:
                if point_idx < len(landmarks.landmark):
                    landmark = landmarks.landmark[point_idx]
                    x = landmark.x * width
                    y = landmark.y * height
                    z = landmark.z if hasattr(landmark, 'z') else 0
                    features.extend([x, y, z])
            
            if len(features) > 128:
                features = features[:128]
            elif len(features) < 128:
                features.extend([0.0] * (128 - len(features)))
            
            features = np.array(features, dtype=np.float64)
            if np.linalg.norm(features) > 0:
                features = features / np.linalg.norm(features)
            
            return features
            
        except Exception as e:
            print(f"❌ Error extracting face encoding: {e}")
            return np.zeros(128, dtype=np.float64)
    
    def _create_basic_encoding(self, face_region: np.ndarray) -> np.ndarray:
        """
        Create basic face encoding from face region when landmarks are not available
        """
        try:
            if face_region.size == 0:
                return np.zeros(128, dtype=np.float64)
            
            face_resized = cv2.resize(face_region, (64, 64))
            
            if len(face_resized.shape) == 3:
                face_gray = cv2.cvtColor(face_resized, cv2.COLOR_RGB2GRAY)
            else:
                face_gray = face_resized
            
            # 1. Histogram features
            hist = cv2.calcHist([face_gray], [0], None, [32], [0, 256])
            hist_features = hist.flatten()
            
            # 2. LBP-like features 
            lbp_features = self._simple_lbp(face_gray)
            
            # 3. Edge features
            edges = cv2.Canny(face_gray, 100, 200)
            edge_features = np.sum(edges, axis=0)[:32] 
            

            all_features = np.concatenate([hist_features, lbp_features, edge_features])
            
            if len(all_features) > 128:
                all_features = all_features[:128]
            elif len(all_features) < 128:
                padding = np.zeros(128 - len(all_features))
                all_features = np.concatenate([all_features, padding])
            
            features = all_features.astype(np.float64)
            if np.linalg.norm(features) > 0:
                features = features / np.linalg.norm(features)
            
            return features
            
        except Exception as e:
            print(f"❌ Error creating basic encoding: {e}")
            return np.zeros(128, dtype=np.float64)
    
    def _simple_lbp(self, image: np.ndarray, radius: int = 1, n_points: int = 8) -> np.ndarray:
        """
        Simplified Local Binary Pattern feature extraction
        """
        try:
            height, width = image.shape
            lbp = np.zeros((height, width), dtype=np.uint8)
            
            for i in range(radius, height - radius):
                for j in range(radius, width - radius):
                    center = image[i, j]
                    code = 0
                    
                    neighbors = [
                        image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                        image[i, j+1], image[i+1, j+1], image[i+1, j],
                        image[i+1, j-1], image[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            code |= (1 << k)
                    
                    lbp[i, j] = code
            
            hist, _ = np.histogram(lbp.ravel(), bins=32, range=[0, 256])
            return hist.astype(np.float64)
            
        except Exception as e:
            print(f"❌ LBP error: {e}")
            return np.zeros(32, dtype=np.float64)
    
    def compare_faces(self, known_encodings: List[np.ndarray], face_encoding: np.ndarray, tolerance: float = 0.6) -> List[bool]:
        """
        Compare face encoding against known encodings
        Returns list of boolean matches
        """
        try:
            if not known_encodings or face_encoding is None:
                return []
            
            distances = []
            for known_encoding in known_encodings:
                dot_product = np.dot(known_encoding, face_encoding)
                norm_product = np.linalg.norm(known_encoding) * np.linalg.norm(face_encoding)
                
                if norm_product == 0:
                    distance = 1.0
                else:
                    similarity = dot_product / norm_product
                    distance = 1.0 - similarity
                
                distances.append(distance)
            
            return [distance <= tolerance for distance in distances]
            
        except Exception as e:
            print(f"❌ Face comparison error: {e}")
            return [False] * len(known_encodings)
    
    def face_distance(self, known_encodings: List[np.ndarray], face_encoding: np.ndarray) -> List[float]:
        """
        Calculate distances between face encoding and known encodings
        """
        try:
            if not known_encodings or face_encoding is None:
                return []
            
            distances = []
            for known_encoding in known_encodings:
                dot_product = np.dot(known_encoding, face_encoding)
                norm_product = np.linalg.norm(known_encoding) * np.linalg.norm(face_encoding)
                
                if norm_product == 0:
                    distance = 1.0
                else:
                    similarity = dot_product / norm_product
                    distance = 1.0 - similarity
                
                distances.append(distance)
            
            return distances
            
        except Exception as e:
            print(f"❌ Face distance calculation error: {e}")
            return [1.0] * len(known_encodings)
    
    def __del__(self):
        """Cleanup MediaPipe resources"""
        try:
            if hasattr(self, 'face_detection'):
                self.face_detection.close()
            if hasattr(self, 'face_mesh'):
                self.face_mesh.close()
        except:
            pass