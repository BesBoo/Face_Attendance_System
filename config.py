"""
File cấu hình chính cho hệ thống điểm danh
"""

import os
from typing import Dict, Any

"""
File cấu hình chính cho hệ thống điểm danh
"""

import os
from typing import Dict, Any

DATABASE_CONFIG = {
    'server': r'DUCCKY\SQLEXPRESS',
    'database': 'face_attendance',
    'driver': 'SQL Server',
    'trusted_connection': True,
    'connection_timeout': 30,
    'command_timeout': 30
}


FACE_RECOGNITION_CONFIG = {
    'tolerance': 0.6,  
    'face_detection_model': 'hog',  
    'num_jitters': 1,  
    'face_locations_model': 'hog', 
    'min_face_size': (50, 50), 
    'max_faces_per_image': 1, 
    'confidence_threshold': 0.5,
}


CAMERA_CONFIG = {
    'default_camera_index': 0,
    'frame_width': 640,
    'frame_height': 480,
    'fps': 30,
    'buffer_size': 1,
    'auto_exposure': True,
    'brightness': 50,
    'contrast': 50,
}

APP_CONFIG = {
    'window_title': 'Hệ thống điểm danh bằng khuôn mặt',
    'window_width': 1200,
    'window_height': 800,
    'theme': 'default',  
    'language': 'vi', 
    'auto_save_interval': 300, 
    'max_recent_attendance': 20,
    'session_timeout': 3600,  
}

PATHS_CONFIG = {
    'data_directory': 'data',
    'images_directory': 'data/images',
    'encodings_file': 'data/encodings.pkl',
    'logs_directory': 'logs',
    'reports_directory': 'reports',
    'config_directory': 'config',
    'backup_directory': 'backup',
    'temp_directory': 'temp',
}

LOGGING_CONFIG = {
    'level': 'INFO',  
    'log_to_file': True,
    'log_to_console': True,
    'max_log_file_size': 10 * 1024 * 1024,  
    'max_log_files': 10,
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'attendance_log_separate': True,
}

REPORTS_CONFIG = {
    'default_format': 'excel',  
    'auto_cleanup_days': 30,
    'include_photos_in_pdf': False,
    'max_rows_per_page': 50,
    'company_name': 'Your Organization Name',
    'company_address': 'Your Address',
    'logo_path': None,  
}

SECURITY_CONFIG = {
    'enable_user_authentication': False,
    'password_min_length': 6,
    'session_expire_minutes': 60,
    'max_login_attempts': 3,
    'lock_account_minutes': 15,
    'encrypt_database_passwords': True,
}

PERFORMANCE_CONFIG = {
    'face_recognition_workers': 2,
    'database_pool_size': 5,
    'cache_encodings': True,
    'cache_size_mb': 100,
    'process_every_nth_frame': 3,  
    'resize_factor': 0.25,  
}

ATTENDANCE_RULES = {
    'allow_multiple_checkins_per_day': False,
    'late_threshold_minutes': 15,  
    'early_checkin_minutes': 30,  
    'auto_mark_absent_after_minutes': 60,  
    'require_manual_approval_for_late': False,
    'weekend_attendance': False,  
}

UI_CONFIG = {
    'show_confidence_scores': True,
    'show_fps_counter': True,
    'show_face_boxes': True,
    'face_box_thickness': 2,
    'font_scale': 0.6,
    'colors': {
        'known_face': (0, 255, 0),    
        'unknown_face': (0, 0, 255),  
        'late_attendance': (255, 165, 0),  
        'present_attendance': (0, 255, 0),  
        'absent_attendance': (255, 0, 0),   
    },
    'sounds': {
        'enable_sounds': True,
        'success_sound': 'sounds/success.wav',
        'error_sound': 'sounds/error.wav',
        'warning_sound': 'sounds/warning.wav',
    }
}

EMAIL_CONFIG = {
    'enable_email_notifications': False,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_username': '',
    'email_password': '',
    'from_email': '',
    'admin_emails': [],
    'send_daily_reports': False,
    'send_alert_emails': True,
}

BACKUP_CONFIG = {
    'auto_backup': True,
    'backup_interval_days': 7,
    'max_backup_files': 5,
    'backup_encodings': True,
    'backup_database': False,  
    'compress_backups': True,
}

DEBUG_CONFIG = {
    'enable_debug_mode': False,
    'save_debug_images': False,
    'debug_image_path': 'debug/images',
    'show_processing_time': True,
    'verbose_logging': False,
    'enable_profiling': False,
}


def get_absolute_path(relative_path: str) -> str:
    """Chuyển đổi đường dẫn tương đối thành tuyệt đối"""
    if os.path.isabs(relative_path):
        return relative_path
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_root, relative_path)

def ensure_directories_exist():
    """Tạo tất cả thư mục cần thiết"""
    for key, path in PATHS_CONFIG.items():
        if key.endswith('_directory'):
            abs_path = get_absolute_path(path)
            os.makedirs(abs_path, exist_ok=True)

def get_config_value(config_dict: Dict[str, Any], key: str, default=None):
    """Lấy giá trị config với giá trị mặc định"""
    return config_dict.get(key, default)

def update_config_value(config_dict: Dict[str, Any], key: str, value: Any):
    """Cập nhật giá trị config"""
    config_dict[key] = value

def validate_config():
    """Kiểm tra tính hợp lệ của config"""
    errors = []

    if not DATABASE_CONFIG.get('server'):
        errors.append("Database server không được để trống")
    
    if not DATABASE_CONFIG.get('database'):
        errors.append("Database name không được để trống")
    

    tolerance = FACE_RECOGNITION_CONFIG.get('tolerance', 0.6)
    if not 0.1 <= tolerance <= 1.0:
        errors.append("Face recognition tolerance phải trong khoảng 0.1 - 1.0")

    for key, path in PATHS_CONFIG.items():
        if key.endswith('_directory'):
            abs_path = get_absolute_path(path)
            try:
                os.makedirs(abs_path, exist_ok=True)
            except Exception as e:
                errors.append(f"Không thể tạo thư mục {path}: {e}")
    
    return errors

def load_user_config(config_file: str = 'config/user_config.json'):
    """Load cấu hình người dùng từ file"""
    import json
    
    config_path = get_absolute_path(config_file)
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            

            for section, values in user_config.items():
                if section in globals() and isinstance(globals()[section], dict):
                    globals()[section].update(values)
            
            return True
        except Exception as e:
            print(f"Lỗi load user config: {e}")
            return False
    
    return False

def save_user_config(config_file: str = 'config/user_config.json'):
    """Lưu cấu hình người dùng ra file"""
    import json
    
    config_path = get_absolute_path(config_file)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    user_config = {
        'DATABASE_CONFIG': DATABASE_CONFIG,
        'FACE_RECOGNITION_CONFIG': FACE_RECOGNITION_CONFIG,
        'CAMERA_CONFIG': CAMERA_CONFIG,
        'APP_CONFIG': APP_CONFIG,
        'PATHS_CONFIG': PATHS_CONFIG,
        'LOGGING_CONFIG': LOGGING_CONFIG,
        'REPORTS_CONFIG': REPORTS_CONFIG,
        'SECURITY_CONFIG': SECURITY_CONFIG,
        'PERFORMANCE_CONFIG': PERFORMANCE_CONFIG,
        'ATTENDANCE_RULES': ATTENDANCE_RULES,
        'UI_CONFIG': UI_CONFIG,
        'EMAIL_CONFIG': EMAIL_CONFIG,
        'BACKUP_CONFIG': BACKUP_CONFIG,
        'DEBUG_CONFIG': DEBUG_CONFIG,
    }
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Lỗi save user config: {e}")
        return False

def get_database_connection_string() -> str:
    """Tạo connection string cho database"""
    config = DATABASE_CONFIG
    
    if config.get('trusted_connection', True):
        connection_string = (
            f"DRIVER={{{config['driver']}}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection=yes;"
        )
    else:
        connection_string = (
            f"DRIVER={{{config['driver']}}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config.get('username', '')};"
            f"PWD={config.get('password', '')};"
        )
    
    return connection_string


def initialize_config():
    """Khởi tạo config khi import module"""

    ensure_directories_exist()

    load_user_config()
    

    errors = validate_config()
    if errors:
        print("Cảnh báo - Lỗi cấu hình:")
        for error in errors:
            print(f"  - {error}")

initialize_config()

__all__ = [
    'DATABASE_CONFIG',
    'FACE_RECOGNITION_CONFIG', 
    'CAMERA_CONFIG',
    'APP_CONFIG',
    'PATHS_CONFIG',
    'LOGGING_CONFIG',
    'REPORTS_CONFIG',
    'SECURITY_CONFIG',
    'PERFORMANCE_CONFIG',
    'ATTENDANCE_RULES',
    'UI_CONFIG',
    'EMAIL_CONFIG',
    'BACKUP_CONFIG',
    'DEBUG_CONFIG',
    'get_absolute_path',
    'ensure_directories_exist',
    'get_config_value',
    'update_config_value',
    'validate_config',
    'load_user_config',
    'save_user_config',
    'get_database_connection_string',
    'initialize_config'
]