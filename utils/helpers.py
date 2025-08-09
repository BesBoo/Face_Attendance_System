import os
import cv2
import numpy as np
from datetime import datetime, date, time
import re
from typing import Optional, Tuple, List
import json

def ensure_directory_exists(directory_path: str):
    """Tạo thư mục nếu chưa tồn tại"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Đã tạo thư mục: {directory_path}")

def get_current_datetime() -> Tuple[str, str]:
    """
    Lấy ngày và giờ hiện tại
    Returns: (date_str, time_str) định dạng YYYY-MM-DD, HH:MM:SS
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    return date_str, time_str

def format_datetime(dt: datetime) -> str:
    """Format datetime thành string đẹp"""
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def parse_date_string(date_str: str) -> Optional[date]:
    """Parse string thành date object"""
    try:
        # Thử các định dạng khác nhau
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    except Exception:
        return None

def parse_time_string(time_str: str) -> Optional[time]:
    """Parse string thành time object"""
    try:
        formats = ["%H:%M:%S", "%H:%M", "%I:%M %p"]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue
        
        return None
    except Exception:
        return None

def validate_student_id(student_id: str) -> bool:
    """Kiểm tra format student ID"""
    # Student ID phải có ít nhất 3 ký tự, chỉ chứa chữ và số
    if not student_id or len(student_id) < 3:
        return False
    
    return re.match(r'^[A-Za-z0-9]+$', student_id) is not None

def validate_name(name: str) -> bool:
    """Kiểm tra tên hợp lệ"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Chỉ chứa chữ cái, khoảng trắng và một số ký tự đặc biệt
    return re.match(r'^[A-Za-zÀ-ỹ\s\.]+$', name.strip()) is not None

def sanitize_filename(filename: str) -> str:
    """Làm sạch tên file, loại bỏ ký tự không hợp lệ"""
    # Loại bỏ ký tự đặc biệt
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Loại bỏ khoảng trắng thừa
    clean_name = re.sub(r'\s+', '_', clean_name.strip())
    return clean_name

def save_image(image: np.ndarray, filepath: str) -> bool:
    """Lưu ảnh OpenCV"""
    try:
        # Tạo thư mục nếu cần
        directory = os.path.dirname(filepath)
        if directory:
            ensure_directory_exists(directory)
        
        success = cv2.imwrite(filepath, image)
        if success:
            print(f"Đã lưu ảnh: {filepath}")
        return success
    except Exception as e:
        print(f"Lỗi lưu ảnh {filepath}: {e}")
        return False

def load_image(filepath: str) -> Optional[np.ndarray]:
    """Load ảnh từ file"""
    try:
        if not os.path.exists(filepath):
            print(f"File không tồn tại: {filepath}")
            return None
        
        image = cv2.imread(filepath)
        if image is None:
            print(f"Không thể đọc ảnh: {filepath}")
            return None
        
        return image
    except Exception as e:
        print(f"Lỗi load ảnh {filepath}: {e}")
        return None

def resize_image(image: np.ndarray, max_width: int = 800, max_height: int = 600) -> np.ndarray:
    """Resize ảnh giữ tỷ lệ"""
    try:
        h, w = image.shape[:2]
        
        # Tính tỷ lệ scale
        scale_w = max_width / w
        scale_h = max_height / h
        scale = min(scale_w, scale_h, 1.0)  # Không phóng to
        
        if scale < 1.0:
            new_width = int(w * scale)
            new_height = int(h * scale)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized
        
        return image
    except Exception as e:
        print(f"Lỗi resize ảnh: {e}")
        return image

def crop_face_region(image: np.ndarray, face_location: Tuple[int, int, int, int], 
                    padding: int = 20) -> Optional[np.ndarray]:
    """
    Cắt vùng khuôn mặt từ ảnh
    face_location: (top, right, bottom, left) - định dạng face_recognition
    """
    try:
        top, right, bottom, left = face_location
        h, w = image.shape[:2]
        
        # Thêm padding và đảm bảo trong giới hạn ảnh
        top = max(0, top - padding)
        left = max(0, left - padding)
        bottom = min(h, bottom + padding)
        right = min(w, right + padding)
        
        # Cắt ảnh
        cropped = image[top:bottom, left:right]
        
        if cropped.size == 0:
            return None
        
        return cropped
    except Exception as e:
        print(f"Lỗi cắt vùng khuôn mặt: {e}")
        return None

def calculate_face_area(face_location: Tuple[int, int, int, int]) -> int:
    """Tính diện tích khuôn mặt"""
    top, right, bottom, left = face_location
    width = right - left
    height = bottom - top
    return width * height

def filter_large_faces(face_locations: List[Tuple[int, int, int, int]], 
                      min_area: int = 2500) -> List[Tuple[int, int, int, int]]:
    """Lọc các khuôn mặt đủ lớn"""
    return [loc for loc in face_locations if calculate_face_area(loc) >= min_area]

def get_image_info(filepath: str) -> dict:
    """Lấy thông tin ảnh"""
    info = {
        'exists': False,
        'size_bytes': 0,
        'dimensions': None,
        'format': None
    }
    
    try:
        if os.path.exists(filepath):
            info['exists'] = True
            info['size_bytes'] = os.path.getsize(filepath)
            
            # Đọc ảnh để lấy thông tin
            image = cv2.imread(filepath)
            if image is not None:
                h, w, c = image.shape
                info['dimensions'] = (w, h, c)
                
                # Xác định format từ extension
                ext = os.path.splitext(filepath)[1].lower()
                format_map = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', 
                             '.bmp': 'BMP', '.tiff': 'TIFF', '.tif': 'TIFF'}
                info['format'] = format_map.get(ext, 'Unknown')
    
    except Exception as e:
        info['error'] = str(e)
    
    return info

def create_thumbnail(image: np.ndarray, size: Tuple[int, int] = (150, 150)) -> np.ndarray:
    """Tạo thumbnail từ ảnh"""
    try:
        return cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    except Exception as e:
        print(f"Lỗi tạo thumbnail: {e}")
        return image

def save_config(config_dict: dict, filepath: str) -> bool:
    """Lưu cấu hình vào file JSON"""
    try:
        ensure_directory_exists(os.path.dirname(filepath))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
        
        print(f"Đã lưu config: {filepath}")
        return True
    except Exception as e:
        print(f"Lỗi lưu config: {e}")
        return False

def load_config(filepath: str, default_config: dict = None) -> dict:
    """Load cấu hình từ file JSON"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Đã load config: {filepath}")
            return config
        else:
            print(f"File config không tồn tại: {filepath}")
            return default_config or {}
    except Exception as e:
        print(f"Lỗi load config: {e}")
        return default_config or {}

def format_file_size(size_bytes: int) -> str:
    """Format kích thước file thành string đẹp"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_available_cameras() -> List[int]:
    """Tìm các camera khả dụng"""
    available_cameras = []
    
    # Test từ camera 0 đến 5
    for i in range(6):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        except Exception:
            continue
    
    return available_cameras

def test_camera(camera_index: int, test_duration: int = 3) -> bool:
    """Test camera có hoạt động không"""
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return False
        
        # Test read một vài frame
        success_count = 0
        for _ in range(test_duration):
            ret, frame = cap.read()
            if ret and frame is not None:
                success_count += 1
        
        cap.release()
        return success_count > 0
        
    except Exception:
        return False

def get_system_info() -> dict:
    """Lấy thông tin hệ thống"""
    import platform
    import psutil
    
    info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'disk_usage': {}
    }
    
    # Thông tin ổ đĩa
    try:
        disk_usage = psutil.disk_usage('/')
        info['disk_usage'] = {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free
        }
    except Exception:
        pass
    
    return info

def cleanup_old_files(directory: str, days_old: int = 30, file_pattern: str = "*") -> int:
    """Xóa các file cũ trong thư mục"""
    import glob
    from datetime import datetime, timedelta
    
    if not os.path.exists(directory):
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_count = 0
    
    try:
        pattern = os.path.join(directory, file_pattern)
        files = glob.glob(pattern)
        
        for filepath in files:
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"Đã xóa file cũ: {filepath}")
    
    except Exception as e:
        print(f"Lỗi cleanup files: {e}")
    
    return deleted_count

def create_backup_filename(original_filepath: str, suffix: str = None) -> str:
    """Tạo tên file backup"""
    directory = os.path.dirname(original_filepath)
    filename = os.path.basename(original_filepath)
    name, ext = os.path.splitext(filename)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if suffix:
        backup_name = f"{name}_{suffix}_{timestamp}{ext}"
    else:
        backup_name = f"{name}_backup_{timestamp}{ext}"
    
    return os.path.join(directory, backup_name)

def convert_cv2_to_rgb(image: np.ndarray) -> np.ndarray:
    """Chuyển ảnh OpenCV (BGR) sang RGB"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def convert_rgb_to_cv2(image: np.ndarray) -> np.ndarray:
    """Chuyển ảnh RGB sang OpenCV (BGR)"""
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def add_text_overlay(image: np.ndarray, text: str, position: Tuple[int, int], 
                    font_scale: float = 0.7, color: Tuple[int, int, int] = (255, 255, 255),
                    thickness: int = 2, background_color: Tuple[int, int, int] = None) -> np.ndarray:
    """Thêm text lên ảnh với background tùy chọn"""
    try:
        # Copy ảnh để không thay đổi ảnh gốc
        result = image.copy()
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Tính kích thước text
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Vẽ background nếu được chỉ định
        if background_color:
            x, y = position
            # Vẽ hình chữ nhật làm nền
            cv2.rectangle(result, 
                         (x - 5, y - text_height - 5), 
                         (x + text_width + 5, y + baseline + 5),
                         background_color, -1)
        
        # Vẽ text
        cv2.putText(result, text, position, font, font_scale, color, thickness)
        
        return result
        
    except Exception as e:
        print(f"Lỗi thêm text overlay: {e}")
        return image