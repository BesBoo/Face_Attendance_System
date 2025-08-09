import cv2
import face_recognition
import numpy as np
from typing import List, Tuple, Optional
import logging

class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def detect_faces_opencv(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Phát hiện khuôn mặt sử dụng OpenCV Cascade
        Returns: List of (x, y, w, h) tuples
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces.tolist()
    
    def detect_faces_fr(self, frame) -> List[Tuple[int, int, int, int]]:
        """
        Phát hiện khuôn mặt sử dụng face_recognition
        Returns: List of (top, right, bottom, left) tuples - định dạng face_recognition
        """
        try:
            # Ensure frame is in correct format
            if frame is None:
                logging.error("Frame is None")
                return []
            
            # Ensure frame is 8-bit
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            
            # Ensure frame has 3 channels (BGR)
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                logging.error(f"Invalid frame shape: {frame.shape}")
                return []
            
            # Only resize if frame is large, and never below 320x240
            min_height, min_width = 150, 150
            height, width = frame.shape[:2]
            if height < min_height or width < min_width:
                logging.error(f"Frame too small for face detection: {frame.shape}")
                return []
            if width > 640 or height > 480:
                scale = min(640 / width, 480 / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                small_frame = cv2.resize(frame, (new_width, new_height))
            else:
                small_frame = frame.copy()
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Ensure RGB frame is also 8-bit
            if rgb_small_frame.dtype != np.uint8:
                rgb_small_frame = rgb_small_frame.astype(np.uint8)
            
            # Additional validation for face_recognition
            if rgb_small_frame.min() < 0 or rgb_small_frame.max() > 255:
                logging.error(f"Invalid pixel values: min={rgb_small_frame.min()}, max={rgb_small_frame.max()}")
                return []
            
            # Debug: Print frame info
            print(f"Face detector - Frame shape: {rgb_small_frame.shape}, dtype: {rgb_small_frame.dtype}, min: {rgb_small_frame.min()}, max: {rgb_small_frame.max()}")
            
            # Tìm khuôn mặt
            try:
                face_locations = face_recognition.face_locations(rgb_small_frame)
            except Exception as e:
                logging.error(f"face_recognition error: {e}. Frame info: shape={rgb_small_frame.shape}, dtype={rgb_small_frame.dtype}, min={rgb_small_frame.min()}, max={rgb_small_frame.max()}")
                return []
            
            # Scale lại tọa độ về kích thước gốc
            face_locations = [(top*4, right*4, bottom*4, left*4) 
                            for (top, right, bottom, left) in face_locations]
            
            return face_locations
            
        except Exception as e:
            logging.error(f"Lỗi phát hiện khuôn mặt: {e}")
            return []
    
    def get_face_encodings(self, frame, face_locations: List[Tuple[int, int, int, int]]) -> List[np.ndarray]:
        """
        Trích xuất encodings từ khuôn mặt
        """
        try:
            # Ensure frame is in correct format
            if frame is None:
                logging.error("Frame is None")
                return []
            
            # Ensure frame is 8-bit
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            
            # Ensure frame has 3 channels (BGR)
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                logging.error(f"Invalid frame shape: {frame.shape}")
                return []
            
            # Resize để tăng tốc
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Ensure RGB frame is also 8-bit
            if rgb_small_frame.dtype != np.uint8:
                rgb_small_frame = rgb_small_frame.astype(np.uint8)
            
            # Scale face locations
            small_face_locations = [(int(top/4), int(right/4), int(bottom/4), int(left/4)) 
                                  for (top, right, bottom, left) in face_locations]
            
            # Get encodings
            face_encodings = face_recognition.face_encodings(rgb_small_frame, small_face_locations)
            return face_encodings
            
        except Exception as e:
            logging.error(f"Lỗi trích xuất face encodings: {e}")
            return []
    
    def detect_and_encode(self, frame) -> Tuple[List[Tuple[int, int, int, int]], List[np.ndarray]]:
        """
        Phát hiện khuôn mặt và trích xuất encodings trong một lần
        Returns: (face_locations, face_encodings)
        """
        face_locations = self.detect_faces_fr(frame)
        face_encodings = self.get_face_encodings(frame, face_locations)
        return face_locations, face_encodings
    
    def draw_face_boxes(self, frame, face_locations: List[Tuple[int, int, int, int]], 
                       names: List[str] = None, colors: List[Tuple[int, int, int]] = None):
        """
        Vẽ khung bao quanh khuôn mặt và tên (nếu có)
        face_locations: format (top, right, bottom, left)
        """
        if names is None:
            names = ["Unknown"] * len(face_locations)
        if colors is None:
            colors = [(0, 255, 0)] * len(face_locations)  # Màu xanh lá mặc định
            
        for (top, right, bottom, left), name, color in zip(face_locations, names, colors):
            # Vẽ khung
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Vẽ nền cho text
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Vẽ text
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
        
        return frame
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Tiền xử lý ảnh để cải thiện chất lượng nhận diện
        """
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                logging.error(f"Không thể đọc ảnh: {image_path}")
                return None
            
            # Cải thiện độ sáng và độ t대比
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced_image = cv2.merge([cl, a, b])
            enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_LAB2BGR)
            
            # Giảm noise
            enhanced_image = cv2.bilateralFilter(enhanced_image, 9, 75, 75)
            
            return enhanced_image
            
        except Exception as e:
            logging.error(f"Lỗi tiền xử lý ảnh: {e}")
            return None
    
    def extract_face_from_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Trích xuất khuôn mặt từ ảnh và trả về face encoding
        """
        try:
            # Tiền xử lý ảnh
            image = self.preprocess_image(image_path)
            if image is None:
                return None
            
            # Ensure image is in correct format
            if image.dtype != np.uint8:
                image = image.astype(np.uint8)
            
            # Ensure image has 3 channels (BGR)
            if len(image.shape) != 3 or image.shape[2] != 3:
                logging.error(f"Invalid image shape: {image.shape}")
                return None
            
            # Chuyển sang RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Ensure RGB image is also 8-bit
            if rgb_image.dtype != np.uint8:
                rgb_image = rgb_image.astype(np.uint8)
            
            # Tìm khuôn mặt
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                logging.warning(f"Không tìm thấy khuôn mặt trong ảnh: {image_path}")
                return None
            
            if len(face_locations) > 1:
                logging.warning(f"Tìm thấy nhiều khuôn mặt trong ảnh: {image_path}, chỉ lấy khuôn mặt đầu tiên")
            
            # Lấy encoding của khuôn mặt đầu tiên
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) > 0:
                return face_encodings[0]
            else:
                logging.error(f"Không thể trích xuất face encoding từ: {image_path}")
                return None
                
        except Exception as e:
            logging.error(f"Lỗi trích xuất khuôn mặt từ ảnh: {e}")
            return None
    
    def capture_face_from_camera(self, camera_index: int = 0) -> Optional[np.ndarray]:
        """
        Chụp ảnh khuôn mặt từ camera và trả về face encoding
        """
        cap = cv2.VideoCapture(camera_index)
        # Set camera resolution to 640x480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not cap.isOpened():
            logging.error("Không thể mở camera")
            return None
        
        try:
            face_encoding = None
            capture_count = 0
            max_attempts = 100  # Tối đa 100 frame để tìm khuôn mặt
            
            while face_encoding is None and capture_count < max_attempts:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Hiển thị frame
                display_frame = frame.copy()
                cv2.putText(display_frame, "Nhin vao camera va nhan SPACE de chup", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_frame, "Nhan ESC de thoat", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Tìm và vẽ khuôn mặt
                face_locations = self.detect_faces_fr(frame)
                if face_locations:
                    self.draw_face_boxes(display_frame, face_locations)
                
                cv2.imshow('Chup anh khuon mat', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                elif key == 32 and face_locations:  # SPACE và có khuôn mặt
                    # Trích xuất encoding
                    face_encodings = self.get_face_encodings(frame, face_locations)
                    if face_encodings:
                        face_encoding = face_encodings[0]
                        cv2.putText(display_frame, "Da chup thanh cong!", 
                                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.imshow('Chup anh khuon mat', display_frame)
                        cv2.waitKey(2000)  # Hiển thị thông báo trong 2 giây
                        break
                
                capture_count += 1
            
            return face_encoding
            
        except Exception as e:
            logging.error(f"Lỗi chụp ảnh từ camera: {e}")
            return None
        finally:
            cap.release()
            cv2.destroyAllWindows()