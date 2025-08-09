# face_recognition_modules/recognizer.py
import face_recognition
import numpy as np
import cv2
import json
import os
from typing import List, Dict, Optional, Tuple
import logging
from .face_detector import FaceDetector

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.known_face_student_ids = []
        self.face_detector = FaceDetector()
        self.tolerance = 0.6
        self.load_known_faces()
    
    def set_tolerance(self, tolerance: float):
        """Đặt ngưỡng chấp nhận cho face recognition"""
        self.tolerance = tolerance
        print(f"Face recognition tolerance set to: {tolerance}")
    
    def load_known_faces(self):
        """Load known faces from saved data"""
        try:
            # Try to load from both JSON file and image directory
            self._load_from_json()
            self._load_from_images()
            
            print(f"Loaded {len(self.known_face_encodings)} known faces")
            
        except Exception as e:
            print(f"Error loading known faces: {e}")
            logging.error(f"Error loading known faces: {e}")
    
    def add_face_from_camera(self, name: str, user_id: int, student_id: str, camera_index: int = 0) -> bool:
        """Add a new face from camera capture"""
        try:
            encoding = self.face_detector.capture_face_from_camera(camera_index)
            if encoding is not None:
                self.save_face_encoding(name, user_id, student_id, encoding)
                return True
            return False
            
        except Exception as e:
            print(f"Error adding face from camera: {e}")
            return False
    
    def add_face_from_image(self, name: str, user_id: int, student_id: str, image_path: str) -> bool:
        """Add a new face from image file"""
        try:
            encoding = self.face_detector.extract_face_from_image(image_path)
            if encoding is not None:
                self.save_face_encoding(name, user_id, student_id, encoding)
                return True
            return False
            
        except Exception as e:
            print(f"Error adding face from image: {e}")
            return False
    
    def update_face_encoding(self, user_id: int, new_encoding: np.ndarray) -> bool:
        """Update existing face encoding"""
        try:
            # Find user index
            user_index = None
            for i, uid in enumerate(self.known_face_ids):
                if uid == user_id:
                    user_index = i
                    break
            
            if user_index is not None:
                self.known_face_encodings[user_index] = new_encoding
                self._save_to_json()
                return True
            else:
                print(f"User with ID {user_id} not found")
                return False
                
        except Exception as e:
            print(f"Error updating face encoding: {e}")
            return False
    
    def remove_face_encoding(self, user_id: int) -> bool:
        """Remove face encoding for a user"""
        try:
            # Find and remove user
            indices_to_remove = []
            for i, uid in enumerate(self.known_face_ids):
                if uid == user_id:
                    indices_to_remove.append(i)
            
            # Remove in reverse order to maintain indices
            for i in reversed(indices_to_remove):
                del self.known_face_encodings[i]
                del self.known_face_names[i]
                del self.known_face_ids[i]
                del self.known_face_student_ids[i]
            
            if indices_to_remove:
                self._save_to_json()
                print(f"Removed {len(indices_to_remove)} face encodings for user ID {user_id}")
                return True
            else:
                print(f"No face encodings found for user ID {user_id}")
                return False
                
        except Exception as e:
            print(f"Error removing face encoding: {e}")
            return False
    
    def get_recognition_stats(self) -> Dict:
        """Get recognition statistics"""
        return {
            'total_known_faces': len(self.known_face_encodings),
            'known_names': self.known_face_names.copy(),
            'tolerance': self.tolerance
        }
    
    def retrain_model(self) -> bool:
        """Retrain the recognition model by reloading all faces"""
        try:
            print("Retraining face recognition model...")
            
            # Clear current data
            self.known_face_encodings.clear()
            self.known_face_names.clear()
            self.known_face_ids.clear()
            self.known_face_student_ids.clear()
            
            # Reload all faces
            self.load_known_faces()
            
            print(f"Model retrained with {len(self.known_face_encodings)} faces")
            return True
            
        except Exception as e:
            print(f"Error retraining model: {e}")
            logging.error(f"Error retraining model: {e}")
            return False
    
    def validate_face_quality(self, frame, min_face_size: int = 50) -> Tuple[bool, str]:
        """
        Validate face quality for recognition
        Returns: (is_valid, message)
        """
        try:
            face_locations = self.face_detector.detect_faces_fr(frame)
            
            if len(face_locations) == 0:
                return False, "Không tìm thấy khuôn mặt"
            
            if len(face_locations) > 1:
                return False, "Tìm thấy nhiều khuôn mặt, vui lòng chỉ có 1 người"
            
            # Check face size
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top
            
            if face_width < min_face_size or face_height < min_face_size:
                return False, f"Khuôn mặt quá nhỏ (tối thiểu {min_face_size}x{min_face_size}px)"
            
            # Check face position (should not be too close to edges)
            frame_height, frame_width = frame.shape[:2]
            margin = 20
            
            if (left < margin or top < margin or 
                right > frame_width - margin or bottom > frame_height - margin):
                return False, "Khuôn mặt quá gần viền ảnh"
            
            return True, "Chất lượng khuôn mặt tốt"
            
        except Exception as e:
            return False, f"Lỗi kiểm tra chất lượng: {str(e)}"
    
    def benchmark_recognition(self, test_images: List[str]) -> Dict:
        """
        Benchmark recognition accuracy with test images
        """
        results = {
            'total_tests': 0,
            'correct_recognitions': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'accuracy': 0.0
        }
        
        try:
            for image_path in test_images:
                if not os.path.exists(image_path):
                    continue
                
                # Load test image
                test_frame = cv2.imread(image_path)
                if test_frame is None:
                    continue
                
                # Recognize faces
                recognition_results = self.recognize_faces(test_frame)
                
                results['total_tests'] += 1
                
                # This is a simplified benchmark - you would need ground truth labels
                # for proper evaluation
                if recognition_results:
                    for result in recognition_results:
                        if result['name'] != 'Unknown':
                            results['correct_recognitions'] += 1
                        else:
                            results['false_negatives'] += 1
            
            if results['total_tests'] > 0:
                results['accuracy'] = results['correct_recognitions'] / results['total_tests']
            
            return results
            
        except Exception as e:
            print(f"Error in benchmark: {e}")
            return results
    
    def _load_from_json(self):
        """Load face data from JSON file"""
        json_file = "data/face_encodings.json"
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for person in data:
                    encoding = np.array(person['encoding'])
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(person['name'])
                    self.known_face_ids.append(person.get('id', 0))
                    self.known_face_student_ids.append(person.get('student_id', ''))
                
                print(f" Successfully ! Loaded {len(data)} faces from JSON file")
                
            except Exception as e:
                print(f"Error loading JSON file: {e}")
    
    def _load_from_images(self):
        """Load face data from image directories"""
        base_dir = "data/images"
        if not os.path.exists(base_dir):
            return
        
        users_file = "data/users.json"
        users_data = {}
        
        # Load user information
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_list = json.load(f)
                    for user in users_list:
                        users_data[f"user_{user['id']}"] = user
            except Exception as e:
                print(f"Error loading users file: {e}")
        
        # Process each user directory
        for user_dir in os.listdir(base_dir):
            user_path = os.path.join(base_dir, user_dir)
            if not os.path.isdir(user_path):
                continue
            
            user_info = users_data.get(user_dir, {})
            user_name = user_info.get('name', user_dir)
            user_id = user_info.get('id', 0)
            student_id = user_info.get('student_id', '')
            
            # Process images in user directory
            encodings_for_user = []
            for image_file in os.listdir(user_path):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(user_path, image_file)
                    
                    # Extract face encoding
                    encoding = self.face_detector.extract_face_from_image(image_path)
                    if encoding is not None:
                        encodings_for_user.append(encoding)
            
            # Add user if we got at least one encoding
            if encodings_for_user:
                # Use average encoding if multiple images
                if len(encodings_for_user) > 1:
                    avg_encoding = np.mean(encodings_for_user, axis=0)
                else:
                    avg_encoding = encodings_for_user[0]
                
                self.known_face_encodings.append(avg_encoding)
                self.known_face_names.append(user_name)
                self.known_face_ids.append(user_id)
                self.known_face_student_ids.append(student_id)
                
                print(f"Loaded user: {user_name} with {len(encodings_for_user)} images")
    
    def save_face_encoding(self, name: str, user_id: int, student_id: str, encoding: np.ndarray):
        """Save a new face encoding"""
        try:
            # Add to current session
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(name)
            self.known_face_ids.append(user_id)
            self.known_face_student_ids.append(student_id)
            
            # Save to JSON file
            self._save_to_json()
            
            print(f"Successfully ! Saved face encoding for: {name}")
            
        except Exception as e:
            print(f"Error saving face encoding: {e}")
            logging.error(f"Error saving face encoding: {e}")
    
    def _save_to_json(self):
        """Save all face encodings to JSON file"""
        json_file = "data/face_encodings.json"
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        
        data = []
        for i in range(len(self.known_face_encodings)):
            person_data = {
                'name': self.known_face_names[i],
                'id': self.known_face_ids[i],
                'student_id': self.known_face_student_ids[i],
                'encoding': self.known_face_encodings[i].tolist()
            }
            data.append(person_data)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def recognize_faces(self, frame) -> List[Dict]:
        """
        Recognize faces in a frame
        Returns: List of dictionaries with recognition results
        """
        results = []
        
        try:
            # Detect faces and get encodings
            face_locations, face_encodings = self.face_detector.detect_and_encode(frame)
            
            if not face_locations:
                return results
            
            # Match faces with known faces
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding, 
                    tolerance=self.tolerance
                )
                
                name = "Unknown"
                user_id = None
                student_id = "Unknown"
                confidence = 0.0
                
                # Find the best match
                if True in matches:
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        user_id = self.known_face_ids[best_match_index]
                        student_id = self.known_face_student_ids[best_match_index]
                        
                        # Calculate confidence (inverse of distance)
                        distance = face_distances[best_match_index]
                        confidence = max(0.0, 1.0 - distance)
                
                result = {
                    'name': name,
                    'user_id': user_id,
                    'student_id': student_id,
                    'confidence': confidence,
                    'location': face_location  # (top, right, bottom, left)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            logging.error(f"Error in face recognition: {e}")
            return results
