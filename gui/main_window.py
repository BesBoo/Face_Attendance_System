# gui/main_window.py - COMPLETE VERSION

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np
from datetime import datetime, date
import json
import sqlite3
import traceback

# Add parent directory to path để import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from database.db import db_manager
except ImportError:
    db_manager = None
    print("Warning: db_manager not found")

# FIXED: Import MediaPipe-based face recognizer instead of face_recognition
try:
    # Try to import the MediaPipe-based recognizer first
    from face_recognition_modules.mediapipe_recognizer import MediaPipeFaceRecognition
    FACE_RECOGNIZER_TYPE = "MediaPipe"
    print("Successfully ! Using MediaPipe-based face recognition")
except ImportError:
    try:
        # Fallback to original recognizer
        from face_recognition_modules.recognizer import FaceRecognizer
        FACE_RECOGNIZER_TYPE = "Original"
        print("Warning !  Using original face_recognition (may have image type issues)")
    except ImportError:
        FaceRecognizer = None
        MediaPipeFaceRecognition = None
        FACE_RECOGNIZER_TYPE = None
        print("❌ No face recognition modules found")

try:
    from utils.logger import app_logger, log_user_action, log_system_event
except ImportError:
    def log_system_event(event_type, message):
        print(f"[{event_type}] {message}")
    def log_user_action(action, details):
        print(f"[USER_ACTION] {action}: {details}")
    app_logger = None

try:
    from utils.helpers import get_current_datetime, get_available_cameras
except ImportError:
    def get_current_datetime():
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
    
    def get_available_cameras():
        """Tìm các camera có sẵn một cách an toàn"""
        available = []
        
        # Kiểm tra tối đa 10 camera index
        for i in range(10):
            cap = None
            try:
                # Tạo VideoCapture với timeout
                cap = cv2.VideoCapture(i)
                
                # Kiểm tra xem camera có thể mở được không
                if cap.isOpened():
                    # Thử đọc 1 frame để đảm bảo camera hoạt động
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        available.append(i)
                        print(f"Camera {i}: Available")
                    else:
                        print(f"Camera {i}: Cannot read frame")
                else:
                    pass
                    
            except Exception as e:
                print(f"Camera {i}: Error - {e}")
                pass
            finally:
                if cap is not None:
                    cap.release()
        
        if not available:
            try:
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        available = [0]
                        print("Default camera 0: Available")
                cap.release()
            except:
                pass
        
        print(f"Available cameras: {available}")
        return available if available else [0]

# FIXED: Enhanced Image Processing Functions
def ensure_valid_image_format(image):
    """
    Đảm bảo hình ảnh có định dạng hợp lệ cho face recognition
    Fixes: "Unsupported image type, must be 8bit gray or RGB image"
    """
    if image is None:
        raise ValueError("Image is None")
    
    # Kiểm tra số chiều
    if len(image.shape) not in [2, 3]:
        raise ValueError(f"Invalid image dimensions: {image.shape}")
    
    # Convert to uint8 if necessary
    if image.dtype != np.uint8:
        print(f"Converting image from {image.dtype} to uint8")
        if image.dtype == np.float32 or image.dtype == np.float64:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        else:
            image = image.astype(np.uint8)
    
    # Handle different color formats
    if len(image.shape) == 2:
        # Grayscale - convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif len(image.shape) == 3:
        channels = image.shape[2]
        if channels == 1:
            # Single channel to RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif channels == 4:
            # RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif channels == 3:
            # Assume BGR, convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Ensure contiguous array
    image = np.ascontiguousarray(image)
    
    print(f"Successfully ! Image format validated: shape={image.shape}, dtype={image.dtype}")
    return image

def safe_face_locations(image):
    """
    Safely detect face locations with proper image format handling
    """
    try:
        # Validate and fix image format
        processed_image = ensure_valid_image_format(image)
        
        # Use appropriate face detection method
        if FACE_RECOGNIZER_TYPE == "MediaPipe":
            # Use MediaPipe-based detection
            mp_recognizer = MediaPipeFaceRecognition()
            locations = mp_recognizer.face_locations(processed_image)
        else:
            # Use original face_recognition with fixed image
            import face_recognition
            locations = face_recognition.face_locations(processed_image)
        
        return locations
        
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        return []

def safe_face_encodings(image, face_locations=None):
    """
    Safely generate face encodings with proper image format handling
    """
    try:
        # Validate and fix image format
        processed_image = ensure_valid_image_format(image)
        
        # Use appropriate face encoding method
        if FACE_RECOGNIZER_TYPE == "MediaPipe":
            # Use MediaPipe-based encoding
            mp_recognizer = MediaPipeFaceRecognition()
            encodings = mp_recognizer.face_encodings(processed_image, face_locations)
        else:
            # Use original face_recognition with fixed image
            import face_recognition
            encodings = face_recognition.face_encodings(processed_image, face_locations)
        
        return encodings
        
    except Exception as e:
        print(f"❌ Face encoding error: {e}")
        return []

# FIXED: Enhanced Face Recognition Wrapper
class SafeFaceRecognizer:
    """
    Enhanced face recognizer wrapper that handles image format issues
    """
    def __init__(self):
        self.recognizer_type = FACE_RECOGNIZER_TYPE
        self.tolerance = 0.6
        self.known_faces = {}
        
        if self.recognizer_type == "MediaPipe":
            self.mp_recognizer = MediaPipeFaceRecognition()
            print("Successfully ! MediaPipe face recognizer initialized")
        else:
            print("Warning  Using fallback face recognition")
    
    def load_known_faces(self):
        """Load known faces from user data"""
        try:
            users_file = "data/users.json"
            if not os.path.exists(users_file):
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            for user in users:
                user_id = user['id']
                user_name = user['name']
                student_id = user.get('student_id', '')
                
                # Load face images for this user
                user_images_dir = f"data/images/user_{user_id}"
                if os.path.exists(user_images_dir):
                    encodings = []
                    for img_file in os.listdir(user_images_dir):
                        if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            img_path = os.path.join(user_images_dir, img_file)
                            try:
                                # FIXED: Load image safely
                                if self.recognizer_type == "MediaPipe":
                                    image = self.mp_recognizer.load_image_file(img_path)
                                else:
                                    image = cv2.imread(img_path)
                                    image = ensure_valid_image_format(image)
                                
                                # Generate encoding
                                face_encodings = safe_face_encodings(image)
                                if face_encodings:
                                    encodings.extend(face_encodings)
                                    
                            except Exception as e:
                                print(f"❌ Error loading image {img_path}: {e}")
                                continue
                    
                    if encodings:
                        self.known_faces[user_id] = {
                            'name': user_name,
                            'student_id': student_id,
                            'encodings': encodings
                        }
                        print(f"Successfully ! Loaded {len(encodings)} encodings for {user_name}")
            
            print(f"Successfully ! Loaded faces for {len(self.known_faces)} users")
            
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
    
    def recognize_faces(self, frame):
        """
        Recognize faces in frame with enhanced error handling
        """
        results = []
        
        try:
            # FIXED: Ensure frame is in correct format
            if frame is None:
                return results
            
            # Validate frame format
            processed_frame = ensure_valid_image_format(frame)
            
            # Detect face locations
            face_locations = safe_face_locations(processed_frame)
            
            if not face_locations:
                return results
            
            # Generate encodings for detected faces
            face_encodings = safe_face_encodings(processed_frame, face_locations)
            
            # Compare with known faces
            for i, (face_encoding, location) in enumerate(zip(face_encodings, face_locations)):
                best_match = None
                best_distance = float('inf')
                
                for user_id, user_data in self.known_faces.items():
                    for known_encoding in user_data['encodings']:
                        # Calculate distance
                        if self.recognizer_type == "MediaPipe":
                            distance = 1 - np.dot(known_encoding, face_encoding)
                        else:
                            import face_recognition
                            distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                        
                        if distance < best_distance:
                            best_distance = distance
                            best_match = user_data
                
                # Determine if match is good enough
                if best_match and best_distance < self.tolerance:
                    results.append({
                        'user_id': user_id,
                        'name': best_match['name'],
                        'student_id': best_match['student_id'],
                        'confidence': 1.0 - best_distance,
                        'location': location
                    })
                else:
                    results.append({
                        'user_id': None,
                        'name': 'Unknown',
                        'student_id': 'Unknown',
                        'confidence': 0.0,
                        'location': location
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Face recognition error: {e}")
            import traceback
            traceback.print_exc()
            return results
    
    def set_tolerance(self, tolerance):
        """Set recognition tolerance"""
        self.tolerance = tolerance

# Dialog Classes
class UserManagementDialog(QDialog):
    """Dialog for managing users"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quản lý người dùng")
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.add_user_btn = QPushButton("Thêm người dùng")
        self.edit_user_btn = QPushButton("Sửa")
        self.delete_user_btn = QPushButton("Xóa")
        self.refresh_btn = QPushButton("Làm mới")
        
        toolbar.addWidget(self.add_user_btn)
        toolbar.addWidget(self.edit_user_btn)
        toolbar.addWidget(self.delete_user_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Tên", "Mã SV", "Ngày tạo"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.users_table)
        
        # Buttons
        buttons = QHBoxLayout()
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.close)
        buttons.addStretch()
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
        # Connect signals
        self.add_user_btn.clicked.connect(self.add_user)
        self.refresh_btn.clicked.connect(self.load_users)
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            users_file = "data/users.json"
            if not os.path.exists(users_file):
                return
            
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
                self.users_table.setItem(row, 1, QTableWidgetItem(user['name']))
                self.users_table.setItem(row, 2, QTableWidgetItem(user.get('student_id', '')))
                self.users_table.setItem(row, 3, QTableWidgetItem(user.get('created_date', '')))
                
        except Exception as e:
            print(f"Error loading users: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách người dùng: {str(e)}")
    
    def add_user(self):
        """Open add user dialog"""
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

class AddUserDialog(QDialog):
    """Dialog for adding new user with face capture"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm người dùng mới")
        self.setModal(True)
        self.resize(900, 700)
        
        self.camera_capture = None
        self.camera_running = False
        self.camera_timer = QTimer()
        self.captured_images = []
        
        self.init_ui()
        self.camera_timer.timeout.connect(self.update_camera_preview)
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left panel - User info
        left_panel = QVBoxLayout()
        
        form_group = QGroupBox("Thông tin người dùng")
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.student_id_input = QLineEdit()
        
        form_layout.addRow("Họ tên:", self.name_input)
        form_layout.addRow("Mã sinh viên:", self.student_id_input)
        
        form_group.setLayout(form_layout)
        left_panel.addWidget(form_group)
        
        # Camera group
        camera_group = QGroupBox("Camera")
        camera_layout = QVBoxLayout()
        
        # Camera controls
        camera_controls = QHBoxLayout()
        self.start_camera_btn = QPushButton("Bật camera")
        self.stop_camera_btn = QPushButton("Tắt camera")
        self.capture_btn = QPushButton("Chụp ảnh")
        
        self.start_camera_btn.clicked.connect(self.start_camera)
        self.stop_camera_btn.clicked.connect(self.stop_camera)
        self.capture_btn.clicked.connect(self.capture_face)
        
        camera_controls.addWidget(self.start_camera_btn)
        camera_controls.addWidget(self.stop_camera_btn)
        camera_controls.addWidget(self.capture_btn)
        
        camera_layout.addLayout(camera_controls)
        
        # Camera display
        self.camera_label = QLabel("Camera chưa được bật")
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setStyleSheet("border: 1px solid gray;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.camera_label)
        
        camera_group.setLayout(camera_layout)
        left_panel.addWidget(camera_group)
        
        layout.addLayout(left_panel)
        
        # Right panel - Captured images
        right_panel = QVBoxLayout()
        
        images_group = QGroupBox("Ảnh đã chụp")
        images_layout = QVBoxLayout()
        
        # Scroll area for images
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.images_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        images_layout.addWidget(scroll)
        images_group.setLayout(images_layout)
        right_panel.addWidget(images_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        
        save_btn.clicked.connect(self.save_user)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        right_panel.addLayout(buttons_layout)
        
        layout.addLayout(right_panel)
        self.setLayout(layout)
    
    def start_camera(self):
        """Start camera preview"""
        try:
            available_cameras = get_available_cameras()
            if not available_cameras:
                QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy camera!")
                return
            
            self.camera_capture = cv2.VideoCapture(available_cameras[0])
            if not self.camera_capture.isOpened():
                QMessageBox.critical(self, "Lỗi", "Không thể mở camera!")
                return
            
            self.camera_running = True
            self.camera_timer.start(30)  # 30ms = ~33 FPS
            
            self.start_camera_btn.setEnabled(False)
            self.stop_camera_btn.setEnabled(True)
            self.capture_btn.setEnabled(True)
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khởi động camera: {str(e)}")
    
    def stop_camera(self):
        """Stop camera preview"""
        self.camera_running = False
        self.camera_timer.stop()
        
        if self.camera_capture:
            self.camera_capture.release()
            self.camera_capture = None
        
        self.camera_label.setText("Camera đã tắt")
        
        self.start_camera_btn.setEnabled(True)
        self.stop_camera_btn.setEnabled(False)
        self.capture_btn.setEnabled(False)
    
    def update_camera_preview(self):
        """Update camera preview"""
        if not self.camera_running or not self.camera_capture:
            return
        
        try:
            ret, frame = self.camera_capture.read()
            if ret:
                # Convert to RGB and display
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale to label size
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.camera_label.setPixmap(scaled_pixmap)
                
        except Exception as e:
            print(f"Camera preview error: {e}")
    
    def capture_face(self):
        """FIXED: Chụp ảnh khuôn mặt với xử lý định dạng hình ảnh"""
        if not self.camera_running or not self.camera_capture:
            return
        
        ret, frame = self.camera_capture.read()
        if ret:
            try:
                # FIXED: Ensure frame is in correct format before saving
                processed_frame = ensure_valid_image_format(frame)
                
                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"face_{timestamp}.jpg"
                
                # Create thumbnail for display  
                thumbnail = cv2.resize(frame, (80, 60))
                rgb_thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_thumbnail.shape
                qt_image = QImage(rgb_thumbnail.data, w, h, ch * w, QImage.Format_RGB888)
                
                # Store the properly formatted frame
                self.captured_images.append({
                    'filename': filename,
                    'data': processed_frame,  # FIXED: Use processed frame
                    'thumbnail': QPixmap.fromImage(qt_image)
                })
                
                # Display thumbnail
                thumb_label = QLabel()
                thumb_label.setPixmap(QPixmap.fromImage(qt_image))
                thumb_label.setToolTip(f"Ảnh {len(self.captured_images)}")
                self.images_layout.addWidget(thumb_label)
                
                QMessageBox.information(self, "Thành công", f"Đã chụp ảnh {len(self.captured_images)}!")
                
            except Exception as e:
                print(f"❌ Error capturing face: {e}")
                QMessageBox.critical(self, "Lỗi", f"Lỗi chụp ảnh: {str(e)}")
    
    def save_user(self):
        """Save user with captured images"""
        try:
            name = self.name_input.text().strip()
            student_id = self.student_id_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập họ tên!")
                return
            
            if not self.captured_images:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chụp ít nhất 1 ảnh!")
                return
            
            # Create data directories
            os.makedirs("data", exist_ok=True)
            os.makedirs("data/images", exist_ok=True)
            
            # Load existing users
            users_file = "data/users.json"
            users = []
            if os.path.exists(users_file):
                with open(users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            
            # Generate new user ID
            user_id = max([user['id'] for user in users], default=0) + 1
            
            # Save user images
            user_images_dir = f"data/images/user_{user_id}"
            os.makedirs(user_images_dir, exist_ok=True)
            
            for i, img_data in enumerate(self.captured_images):
                img_path = os.path.join(user_images_dir, img_data['filename'])
                # Save as BGR for OpenCV compatibility
                bgr_image = cv2.cvtColor(img_data['data'], cv2.COLOR_RGB2BGR)
                cv2.imwrite(img_path, bgr_image)
            
            # Add user to list
            new_user = {
                'id': user_id,
                'name': name,
                'student_id': student_id,
                'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'image_count': len(self.captured_images)
            }
            
            users.append(new_user)
            
            # Save users file
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Thành công", f"Đã thêm người dùng {name} thành công!")
            self.accept()
            
        except Exception as e:
            print(f"Error saving user: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu người dùng: {str(e)}")
    
    def closeEvent(self, event):
        """Clean up when dialog closes"""
        self.stop_camera()
        event.accept()

# Main Window Class
class AttendanceMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize basic variables first
        self.current_user = None
        self.current_class = None
        self.camera_running = False
        self.camera_timer = QTimer()
        self.camera_capture = None
        
        # FIXED: Initialize enhanced face recognizer
        try:
            self.face_recognizer = SafeFaceRecognizer()
            self.face_recognizer.load_known_faces()
            print("Successfully ! Safe face recognizer initialized")
        except Exception as e:
            print(f"❌ Could not initialize face recognizer: {e}")
            self.face_recognizer = None
        
        # Setup UI and other components
        try:
            self.init_ui()
            self.setup_menu()
            self.setup_toolbar()
            self.setup_status_bar()
            self.connect_database()
            
            # Setup timers
            self.camera_timer.timeout.connect(self.update_camera_frame)
            
            self.time_timer = QTimer()
            self.time_timer.timeout.connect(self.update_current_time)
            self.time_timer.start(1000)
            
            log_system_event("STARTUP", "Ứng dụng điểm danh đã khởi động")
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            traceback.print_exc()
            raise e
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Hệ thống điểm danh bằng nhận dạng khuôn mặt")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Camera and controls
        left_panel = QVBoxLayout()
        
        # Camera group
        camera_group = QGroupBox("Camera")
        camera_layout = QVBoxLayout()
        
        # Camera display
        self.camera_label = QLabel("Camera chưa được bật")
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("border: 2px solid #ccc; background-color: #f0f0f0;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.camera_label)
        
        # Camera controls
        camera_controls = QHBoxLayout()
        self.start_camera_btn = QPushButton("Bật Camera")
        self.stop_camera_btn = QPushButton("Tắt Camera")
        self.camera_combo = QComboBox()
        
        camera_controls.addWidget(QLabel("Camera:"))
        camera_controls.addWidget(self.camera_combo)
        camera_controls.addStretch()
        camera_controls.addWidget(self.start_camera_btn)
        camera_controls.addWidget(self.stop_camera_btn)
        
        camera_layout.addLayout(camera_controls)
        camera_group.setLayout(camera_layout)
        left_panel.addWidget(camera_group)
        
        # Recognition settings
        settings_group = QGroupBox("Cài đặt nhận dạng")
        settings_layout = QFormLayout()
        
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setRange(30, 90)
        self.tolerance_slider.setValue(60)
        self.tolerance_label = QLabel("0.60")
        
        tolerance_layout = QHBoxLayout()
        tolerance_layout.addWidget(self.tolerance_slider)
        tolerance_layout.addWidget(self.tolerance_label)
        
        settings_layout.addRow("Độ nhạy:", tolerance_layout)
        
        self.auto_attendance_cb = QCheckBox("Tự động điểm danh")
        self.auto_attendance_cb.setChecked(True)
        settings_layout.addRow(self.auto_attendance_cb)
        
        settings_group.setLayout(settings_layout)
        left_panel.addWidget(settings_group)
        
        main_layout.addLayout(left_panel)
        
        # Right panel - Attendance info
        right_panel = QVBoxLayout()
        
        # Class info
        class_group = QGroupBox("Thông tin lớp học")
        class_layout = QFormLayout()
        
        self.class_combo = QComboBox()
        self.class_combo.addItems(["Lớp AI", "Lớp CSDL", "Lớp Toán Rời Rạc"])
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["Buổi sáng", "Buổi chiều", "Buổi tối"])
        
        class_layout.addRow("Lớp:", self.class_combo)
        class_layout.addRow("Ngày:", self.date_edit)
        class_layout.addRow("Buổi:", self.session_combo)
        
        class_group.setLayout(class_layout)
        right_panel.addWidget(class_group)
        
        # Attendance list
        attendance_group = QGroupBox("Danh sách điểm danh")
        attendance_layout = QVBoxLayout()
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels([
            "Mã SV", "Họ tên", "Thời gian", "Trạng thái", "Độ tin cậy"
        ])
        self.attendance_table.horizontalHeader().setStretchLastSection(True)
        attendance_layout.addWidget(self.attendance_table)
        
        # Attendance controls
        attendance_controls = QHBoxLayout()
        self.manual_attendance_btn = QPushButton("Điểm danh thủ công")
        self.export_btn = QPushButton("Xuất báo cáo")
        self.clear_btn = QPushButton("Xóa danh sách")
        
        attendance_controls.addWidget(self.manual_attendance_btn)
        attendance_controls.addWidget(self.export_btn)
        attendance_controls.addStretch()
        attendance_controls.addWidget(self.clear_btn)
        
        attendance_layout.addLayout(attendance_controls)
        attendance_group.setLayout(attendance_layout)
        right_panel.addWidget(attendance_group)
        
        # Statistics
        stats_group = QGroupBox("Thống kê")
        stats_layout = QHBoxLayout()
        
        self.total_students_label = QLabel("Tổng: 0")
        self.present_students_label = QLabel("Có mặt: 0")
        self.absent_students_label = QLabel("Vắng: 0")
        
        stats_layout.addWidget(self.total_students_label)
        stats_layout.addWidget(self.present_students_label)
        stats_layout.addWidget(self.absent_students_label)
        stats_layout.addStretch()
        
        stats_group.setLayout(stats_layout)
        right_panel.addWidget(stats_group)
        
        main_layout.addLayout(right_panel)
        central_widget.setLayout(main_layout)
        
        # Connect signals
        self.start_camera_btn.clicked.connect(self.start_camera)
        self.stop_camera_btn.clicked.connect(self.stop_camera)
        self.tolerance_slider.valueChanged.connect(self.update_tolerance)
        
        # Load available cameras
        self.load_available_cameras()
        
        # Initial state
        self.stop_camera_btn.setEnabled(False)
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('Tệp')
        
        new_session_action = QAction('Buổi học mới', self)
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Thoát', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # User menu
        user_menu = menubar.addMenu('Người dùng')
        
        manage_users_action = QAction('Quản lý người dùng', self)
        manage_users_action.triggered.connect(self.open_user_management)
        user_menu.addAction(manage_users_action)
        
        add_user_action = QAction('Thêm người dùng mới', self)
        add_user_action.triggered.connect(self.add_new_user)
        user_menu.addAction(add_user_action)
        
        # Reports menu
        reports_menu = menubar.addMenu('Báo cáo')
        
        export_csv_action = QAction('Xuất CSV', self)
        export_csv_action.triggered.connect(self.export_attendance_csv)
        reports_menu.addAction(export_csv_action)
        
        export_excel_action = QAction('Xuất Excel', self)
        export_excel_action.triggered.connect(self.export_attendance_excel)
        reports_menu.addAction(export_excel_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Cài đặt')
        
        camera_settings_action = QAction('Cài đặt Camera', self)
        camera_settings_action.triggered.connect(self.open_camera_settings)
        settings_menu.addAction(camera_settings_action)
        
        recognition_settings_action = QAction('Cài đặt nhận dạng', self)
        recognition_settings_action.triggered.connect(self.open_recognition_settings)
        settings_menu.addAction(recognition_settings_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = self.addToolBar('Main')
        
        # Camera actions
        start_camera_action = QAction('Bật Camera', self)
        start_camera_action.triggered.connect(self.start_camera)
        toolbar.addAction(start_camera_action)
        
        stop_camera_action = QAction('Tắt Camera', self)
        stop_camera_action.triggered.connect(self.stop_camera)
        toolbar.addAction(stop_camera_action)
        
        toolbar.addSeparator()
        
        # User actions
        add_user_action = QAction('Thêm người dùng', self)
        add_user_action.triggered.connect(self.add_new_user)
        toolbar.addAction(add_user_action)
        
        manage_users_action = QAction('Quản lý người dùng', self)
        manage_users_action.triggered.connect(self.open_user_management)
        toolbar.addAction(manage_users_action)
        
        toolbar.addSeparator()
        
        # Export actions
        export_action = QAction('Xuất báo cáo', self)
        export_action.triggered.connect(self.export_attendance_csv)
        toolbar.addAction(export_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        
        # Status labels
        self.camera_status_label = QLabel("Camera: Tắt")
        self.recognition_status_label = QLabel("Nhận dạng: Sẵn sàng")
        self.time_label = QLabel()
        
        self.status_bar.addWidget(self.camera_status_label)
        self.status_bar.addWidget(self.recognition_status_label)
        self.status_bar.addPermanentWidget(self.time_label)
        
        self.update_current_time()
    
    def connect_database(self):
        """Connect to database"""
        try:
            if db_manager:
                # Test database connection
                log_system_event("DATABASE", "Kết nối cơ sở dữ liệu thành công")
            else:
                log_system_event("DATABASE", "Không có kết nối cơ sở dữ liệu - sử dụng file JSON")
        except Exception as e:
            print(f"Database connection error: {e}")
    
    def load_available_cameras(self):
        """Load available cameras to combo box"""
        try:
            cameras = get_available_cameras()
            self.camera_combo.clear()
            
            for camera_id in cameras:
                self.camera_combo.addItem(f"Camera {camera_id}", camera_id)
                
            if cameras:
                log_system_event("CAMERA", f"Tìm thấy {len(cameras)} camera: {cameras}")
            else:
                log_system_event("CAMERA", "Không tìm thấy camera nào")
                
        except Exception as e:
            print(f"Error loading cameras: {e}")
    
    def start_camera(self):
        """Start camera capture"""
        try:
            if self.camera_running:
                return
            
            # Get selected camera
            camera_id = self.camera_combo.currentData()
            if camera_id is None:
                camera_id = 0
            
            self.camera_capture = cv2.VideoCapture(camera_id)
            
            if not self.camera_capture.isOpened():
                QMessageBox.critical(self, "Lỗi", f"Không thể mở camera {camera_id}!")
                return
            
            # Set camera properties
            self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_capture.set(cv2.CAP_PROP_FPS, 30)
            
            self.camera_running = True
            self.camera_timer.start(33)  # ~30 FPS
            
            self.start_camera_btn.setEnabled(False)
            self.stop_camera_btn.setEnabled(True)
            self.camera_status_label.setText("Camera: Bật")
            
            log_user_action("START_CAMERA", f"Camera {camera_id}")
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khởi động camera: {str(e)}")
    
    def stop_camera(self):
        """Stop camera capture"""
        try:
            self.camera_running = False
            self.camera_timer.stop()
            
            if self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
            
            self.camera_label.setText("Camera đã tắt")
            self.camera_label.setPixmap(QPixmap())
            
            self.start_camera_btn.setEnabled(True)
            self.stop_camera_btn.setEnabled(False)
            self.camera_status_label.setText("Camera: Tắt")
            
            log_user_action("STOP_CAMERA", "Camera stopped")
            
        except Exception as e:
            print(f"Error stopping camera: {e}")
    
    def update_tolerance(self, value):
        """Update face recognition tolerance"""
        tolerance = value / 100.0
        self.tolerance_label.setText(f"{tolerance:.2f}")
        
        if self.face_recognizer:
            self.face_recognizer.set_tolerance(tolerance)
    
    def update_current_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def update_camera_frame(self):
        """FIXED: Cập nhật frame camera với xử lý lỗi đã được sửa"""
        if not self.camera_running or not self.camera_capture:
            return
        
        try:
            ret, frame = self.camera_capture.read()
            if not ret or frame is None:
                return
            
            print(f"[DEBUG] Camera frame: shape={frame.shape}, dtype={frame.dtype}")
            
            # Validate frame size
            if frame.shape[0] < 150 or frame.shape[1] < 150:
                print(f"❌ Frame too small: {frame.shape}")
                self.stop_camera()
                QMessageBox.critical(self, "Lỗi", f"Camera cung cấp độ phân giải quá thấp ({frame.shape}).")
                return
            
            # Create display copy
            display_frame = frame.copy()
            
            # FIXED: Face recognition with proper error handling
            if self.face_recognizer:
                try:
                    # Use the safe face recognizer
                    recognition_results = self.face_recognizer.recognize_faces(frame)
                    
                    # Draw results on display_frame (BGR format)
                    for result in recognition_results:
                        location = result.get('location', [])
                        name = result.get('name', 'Unknown')
                        confidence = result.get('confidence', 0.0)
                        
                        if len(location) == 4:
                            # Color selection
                            color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
                            
                            # Draw bounding box
                            top, right, bottom, left = location
                            cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                            
                            # Draw label
                            text = f"{name} ({confidence:.2f})" if name != 'Unknown' else "Unknown"
                            cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                            cv2.putText(display_frame, text, (left + 6, bottom - 6), 
                                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Process attendance
                    self.process_attendance(recognition_results)
                    
                except Exception as e:
                    print(f"❌ Face recognition error: {e}")
                    # Fallback to simple detection
                    self._use_simple_face_detection(display_frame)
            else:
                # No face recognizer, use simple detection
                self._use_simple_face_detection(display_frame)
            
            # FIXED: Convert and display with error handling
            try:
                rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale and display
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.camera_label.setPixmap(scaled_pixmap)
                
            except Exception as display_error:
                print(f"❌ Display error: {display_error}")
                self.camera_label.setText(f"Display error: {str(display_error)[:50]}...")
                
        except Exception as camera_error:
            print(f"❌ Camera error: {camera_error}")
            self.camera_label.setText(f"Camera error: {str(camera_error)[:50]}...")
    
    def _use_simple_face_detection(self, display_frame):
        """FIXED: Enhanced fallback face detection"""
        try:
            gray = cv2.cvtColor(display_frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display_frame, "Face detected", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.putText(display_frame, f"Faces: {len(faces)} (Simple detection)", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
        except Exception as e:
            print(f"❌ Simple face detection error: {e}")
            cv2.putText(display_frame, f"Detection error", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    
    def process_attendance(self, recognition_results):
        """Process attendance from recognition results"""
        if not self.auto_attendance_cb.isChecked():
            return
        
        try:
            current_time = datetime.now()
            
            for result in recognition_results:
                user_id = result.get('user_id')
                name = result.get('name', 'Unknown')
                student_id = result.get('student_id', 'Unknown')
                confidence = result.get('confidence', 0.0)
                
                if user_id and name != 'Unknown' and confidence > 0.5:
                    # Check if already marked present today
                    if not self.is_already_present(student_id):
                        self.add_attendance_record(student_id, name, current_time, confidence)
                        log_user_action("AUTO_ATTENDANCE", f"{name} ({student_id}) - {confidence:.2f}")
                        
        except Exception as e:
            print(f"Error processing attendance: {e}")
    
    def is_already_present(self, student_id):
        """Check if student is already marked present today"""
        try:
            for row in range(self.attendance_table.rowCount()):
                table_student_id = self.attendance_table.item(row, 0)
                if table_student_id and table_student_id.text() == student_id:
                    return True
            return False
        except:
            return False
    
    def add_attendance_record(self, student_id, name, time, confidence):
        """Add attendance record to table"""
        try:
            row = self.attendance_table.rowCount()
            self.attendance_table.insertRow(row)
            
            self.attendance_table.setItem(row, 0, QTableWidgetItem(student_id))
            self.attendance_table.setItem(row, 1, QTableWidgetItem(name))
            self.attendance_table.setItem(row, 2, QTableWidgetItem(time.strftime("%H:%M:%S")))
            self.attendance_table.setItem(row, 3, QTableWidgetItem("Có mặt"))
            self.attendance_table.setItem(row, 4, QTableWidgetItem(f"{confidence:.2f}"))
            
            # Scroll to bottom
            self.attendance_table.scrollToBottom()
            
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            print(f"Error adding attendance record: {e}")
    
    def update_statistics(self):
        """Update attendance statistics"""
        try:
            total = self.attendance_table.rowCount()
            present = total  # All records in table are present
            absent = 0  # Would need class roster to calculate
            
            self.total_students_label.setText(f"Tổng: {total}")
            self.present_students_label.setText(f"Có mặt: {present}")
            self.absent_students_label.setText(f"Vắng: {absent}")
            
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    # Menu action methods
    def new_session(self):
        """Start new attendance session"""
        reply = QMessageBox.question(self, "Buổi học mới", 
                                   "Bạn có muốn xóa danh sách điểm danh hiện tại?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.attendance_table.setRowCount(0)
            self.update_statistics()
            log_user_action("NEW_SESSION", "Started new attendance session")
    
    def open_user_management(self):
        """Open user management dialog"""
        try:
            dialog = UserManagementDialog(self)
            dialog.exec_()
            
            # Reload face recognizer after user management
            if self.face_recognizer:
                self.face_recognizer.load_known_faces()
                
        except Exception as e:
            print(f"Error opening user management: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể mở quản lý người dùng: {str(e)}")
    
    def add_new_user(self):
        """Open add new user dialog"""
        try:
            dialog = AddUserDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                # Reload face recognizer after adding user
                if self.face_recognizer:
                    self.face_recognizer.load_known_faces()
                    
        except Exception as e:
            print(f"Error opening add user dialog: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể mở dialog thêm người dùng: {str(e)}")
    
    def export_attendance_csv(self):
        """Export attendance to CSV"""
        try:
            if self.attendance_table.rowCount() == 0:
                QMessageBox.information(self, "Thông báo", "Không có dữ liệu để xuất!")
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Xuất CSV", f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write header
                    headers = []
                    for col in range(self.attendance_table.columnCount()):
                        headers.append(self.attendance_table.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Write data
                    for row in range(self.attendance_table.rowCount()):
                        row_data = []
                        for col in range(self.attendance_table.columnCount()):
                            item = self.attendance_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu ra {filename}")
                log_user_action("EXPORT_CSV", filename)
                
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất CSV: {str(e)}")
    
    def export_attendance_excel(self):
        """Export attendance to Excel"""
        QMessageBox.information(self, "Thông báo", "Chức năng xuất Excel sẽ được phát triển trong phiên bản tiếp theo!")
    
    def open_camera_settings(self):
        """Open camera settings dialog"""
        QMessageBox.information(self, "Thông báo", "Chức năng cài đặt camera sẽ được phát triển trong phiên bản tiếp theo!")
    
    def open_recognition_settings(self):
        """Open recognition settings dialog"""
        QMessageBox.information(self, "Thông báo", "Chức năng cài đặt nhận dạng sẽ được phát triển trong phiên bản tiếp theo!")
    
    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Stop camera if running
            if self.camera_running:
                self.stop_camera()
            
            log_system_event("SHUTDOWN", "Ứng dụng đã tắt")
            event.accept()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
            event.accept()

# Main execution
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Face Attendance System")
        app.setOrganizationName("Your Organization")
        
        # Create and show main window
        window = AttendanceMainWindow()
        window.show()
        
        print(" Application started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()