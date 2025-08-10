#  Hệ Thống Điểm Danh Bằng Nhận Dạng Khuôn Mặt

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-orange.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Hệ thống điểm danh thông minh sử dụng công nghệ nhận dạng khuôn mặt, được phát triển bằng Python với giao diện PyQt5.

##  Tính Năng Chính

-  **Nhận dạng khuôn mặt tự động** với độ chính xác cao
-  **Hỗ trợ nhiều camera** USB/Webcam
-  **Quản lý người dùng** dễ dàng với giao diện trực quan
-  **Thống kê điểm danh** real-time
-  **Xuất báo cáo** CSV/Excel
-  **Cài đặt linh hoạt** độ nhạy nhận dạng
-  **Giao diện thân thiện** với người dùng
-  **Lưu trữ dữ liệu** an toàn

##  Giao Diện Ứng Dụng

### Màn Hình Chính

<img width="1194" height="833" alt="Screenshot 2025-08-09 180707" src="https://github.com/user-attachments/assets/fc91aeff-c2ef-4804-b5f6-34423b911bfe" />



### Demo Quá Trình Điểm Danh

1. **Khởi động camera và phát hiện khuôn mặt:**

    Camera ON →  Face Detection →  Recognition → Auto Attendance


2. **Kết quả nhận dạng:**

   <img width="1268" height="834" alt="Screenshot 2025-08-09 180918" src="https://github.com/user-attachments/assets/1a3b18be-0bbd-4f18-811c-a4ef550e6104" />



3. **Cập nhật danh sách tự động:**

   123654 - BesBoo - 18:08:53 - Có mặt


##  Thêm Người Dùng Mới

### Giao Diện Thêm User

<img width="889" height="730" alt="Screenshot 2025-08-09 180821" src="https://github.com/user-attachments/assets/d7232300-79d6-41ea-a418-2a84e283afc3" />



### Quy Trình Thêm User
1. **Nhập thông tin cơ bản:**
   - Họ và tên đầy đủ
   - Mã số sinh viên/nhân viên

2. **Chụp ảnh training:**
   - Bật camera preview
   - Đảm bảo khuôn mặt được phát hiện (khung xanh)
   - Chụp 3-5 ảnh từ các góc độ khác nhau
   - Xem preview các ảnh đã chụp

3. **Lưu dữ liệu:**
   - Hệ thống tự động trích xuất face encodings
   - Lưu vào database/JSON
   - Reload model nhận dạng

##  Cài Đặt và Chạy

### 1. Yêu Cầu Hệ Thống
- **Python:** 3.7 trở lên
- **RAM:** Tối thiểu 4GB
- **Camera:** USB Webcam hoặc camera tích hợp
- **OS:** Windows 10/11, Ubuntu 18.04+, macOS 10.14+

### 2. Cài Đặt Dependencies

```bash

git clone https://github.com/BesBoo/Face_Attendance_System.git
cd face-attendance-system

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3. Cấu Trúc Thư Mục
```
face-attendance-system/
├── main.py                     # File chính khởi động app
├── requirements.txt            # Dependencies
├── README.md                  
├── LICENSE                    
│
├── face_recognition_modules/ 
│   ├── __init__.py
│   ├── face_detector.py     
│   ├── face_encoder.py        
│   └── recognizer.py         
│
├── gui/                       # Giao diện người dùng
│   ├── __init__.py
│   └── main_window.py       
│
├── database/                
│   ├── __init__.py
│   └── db.py
│
├── utils/                    
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
│
└── data/                      
    ├── images/             
    │   ├── user_1/
    │   ├── user_2/
    │   └── ...
    ├── users.json            
    ├── encodings.pkl         
    └── logs/                
```

### 4. Chạy Ứng Dụng

```bash

python main.py

# Hoặc chạy trực tiếp GUI
python -m gui.main_window
```

## ⚙️ Cấu Hình

### Cài Đặt Camera
```python

CAMERA_SETTINGS = {
    'default_camera': 0,        
    'resolution': (640, 480),   
    'fps': 30,                  
    'auto_exposure': True      
}
```

### Cài Đặt Nhận Dạng
```python
RECOGNITION_SETTINGS = {
    'tolerance': 0.6,         
    'model': 'hog',            
    'auto_attendance': True,   
    'confidence_threshold': 0.5 
}
```

##  Tính Năng Nâng Cao

### 1. Xuất Báo Cáo
```python
# Xuất CSV
df = export_attendance_csv(date_from, date_to, class_id)

# Xuất Excel với biểu đồ
export_attendance_excel_with_charts(data, filename)
```

### 2. API Integration
```python
# REST API endpoints
POST /api/users         
GET  /api/attendance     
POST /api/recognition   
```

### 3. Backup & Recovery
```python
# Backup dữ liệu
backup_system_data(backup_path)

# Restore từ backup
restore_from_backup(backup_file)
```

##  Troubleshooting

### Lỗi Camera
```bash
# Kiểm tra camera có sẵn
python -c "import cv2; print([i for i in range(10) if cv2.VideoCapture(i).read()[0]])"

# Nếu không tìm thấy camera
- Kiểm tra driver camera
- Thử các port khác (0, 1, 2...)
- Kiểm tra quyền truy cập camera
```

### Lỗi Face Recognition
```bash
# Cài đặt lại face_recognition
pip uninstall face_recognition
pip install --no-cache-dir face_recognition

# Nếu lỗi trên Windows
pip install cmake
pip install dlib
pip install face_recognition
```

### Lỗi Memory
```bash
# Giảm độ phân giải camera
CAMERA_RESOLUTION = (320, 240)

# Tăng RAM hoặc sử dụng GPU
pip install face_recognition[gpu]
```


##  Changelog

### Version 1.0.0 (2025-07-15)
- ✅ Phiên bản đầu tiên
- ✅ Nhận dạng khuôn mặt, danh tính cơ bản
- ✅ Giao diện PyQt5
- ✅ Quản lý users
- ✅ Xuất CSV




##  Giấy Phép

Dự án này được phát hành dưới giấy phép MIT License. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

##  Lời Cảm Ơn

- [OpenCV](https://opencv.org/) - Computer Vision library
- [face_recognition](https://github.com/ageitgey/face_recognition) - Face recognition library
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [dlib](http://dlib.net/) - Machine learning toolkit
  
## Contact

- **Author**: Trần Duy Đức
- **Email**: tranduyduc9679@gmail.com
- **GitHub**: @BesBoo (https://github.com/BesBoo)
- **Project Link**: [https://github.com/BesBoo/Face-Recognition-System](https://github.com/BesBoo/Face_Attendance_System)
---

 **Nếu dự án này hữu ích, hãy cho tôi một ⭐** 


