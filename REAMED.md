# Hệ thống Điểm danh bằng Khuôn mặt

## Mô tả

Hệ thống điểm danh tự động sử dụng công nghệ nhận diện khuôn mặt được xây dựng bằng Python. Ứng dụng cho phép:

- ✅ **Nhận diện khuôn mặt tự động** qua webcam
- 📊 **Quản lý lớp học và sinh viên** 
- 📈 **Báo cáo điểm danh** chi tiết
- 🎯 **Giao diện thân thiện** với PyQt5
- 🗄️ **Lưu trữ dữ liệu** với SQL Server

## Yêu cầu hệ thống

### Phần cứng
- **CPU**: Intel i5 hoặc tương đương trở lên
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB+)
- **Webcam**: Camera tích hợp hoặc camera USB
- **Ổ cứng**: Ít nhất 2GB dung lượng trống

### Phần mềm
- **Windows 10/11** (64-bit)
- **Python 3.8+** 
- **SQL Server** hoặc **SQL Server Express**
- **Microsoft Visual C++ Redistributable**

## Cài đặt

### Bước 1: Chuẩn bị môi trường

1. **Cài đặt Python 3.8+**
   ```bash
   # Tải từ https://python.org và cài đặt
   # Đảm bảo check "Add Python to PATH"
   ```

2. **Cài đặt SQL Server Express**
   ```
   # Tải từ Microsoft và cài đặt
   # Server name: DUCCKY\SQLEXPRESS (hoặc tương tự)
   # Authentication: Windows Authentication
   ```

3. **Tạo database**
   ```sql
   -- Mở SQL Server Management Studio
   -- Tạo database mới tên "face_attendance"
   CREATE DATABASE face_attendance;
   ```

### Bước 2: Clone project

```bash
git clone <repository-url>
cd face_attendance_system
```

### Bước 3: Cài đặt dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv
venv\Scripts\activate

# Cài đặt các thư viện
pip install -r requirements.txt
```

### Bước 4: Thiết lập database

1. **Chạy script tạo bảng**
   ```bash
   # Mở SQL Server Management Studio
   # Mở file database/setup_db.sql
   # Chạy script để tạo các bảng
   ```

2. **Kiểm tra kết nối**
   ```python
   # Chạy script test
   python test_connection.py
   ```

### Bước 5: Cấu hình hệ thống

1. **Chỉnh sửa config.py**
   ```python
   DATABASE_CONFIG = {
       'server': r'YOUR_SERVER\SQLEXPRESS',  # Thay đổi server name
       'database': 'face_attendance',
       # ... other configs
   }
   ```

2. **Tạo thư mục cần thiết**
   ```bash
   mkdir data data/images logs reports
   ```

## Chạy ứng dụng

```bash
# Kích hoạt virtual environment (nếu có)
venv\Scripts\activate

# Chạy ứng dụng chính
python main.py
```

## Cấu trúc thư mục

```
face_attendance/
├── main.py                     # File khởi động chính
├── config.py                   # Cấu hình hệ thống
├── requirements.txt            # Danh sách thư viện
├── README.md                   # Hướng dẫn này
│
├── gui/                        # Giao diện người dùng
│   ├── main_window.py         # Cửa sổ chính
│   └── attendance_gui.py      # Giao diện điểm danh
│
├── face_recognition/           # Module nhận diện
│   ├── face_detector.py       # Phát hiện khuôn mặt
│   ├── face_encoder.py        # Mã hóa khuôn mặt
│   └── recognizer.py          # Nhận diện
│
├── database/                   # Quản lý database
│   ├── db.py                  # Kết nối và truy vấn
│   ├── models.py              # Models dữ liệu
│   └── setup_db.sql           # Script tạo database
│
├── reports/                    # Tạo báo cáo
│   └── report_generator.py    # Generator báo cáo
│
├── utils/                      # Tiện ích
│   ├── helpers.py             # Hàm hỗ trợ
│   └── logger.py              # Hệ thống logging
│
├── data/                       # Dữ liệu
│   ├── images/                # Ảnh khuôn mặt
│   └── encodings.pkl          # Face encodings
│
├── logs/                       # File log
├── reports/                    # Báo cáo xuất ra
└── config/                     # File cấu hình
```

## Hướng dẫn sử dụng

### 1. Khởi động ứng dụng

1. Chạy `python main.py`
2. Đợi splash screen tải xong
3. Giao diện chính sẽ hiện ra

### 2. Thêm người dùng mới

1. **Menu** → **Quản lý** → **Quản lý người dùng**
2. Nhấn **"Thêm người dùng"**
3. Nhập thông tin: Tên, Mã SV, Vai trò
4. **Chụp ảnh khuôn mặt**:
   - Nhấn "Chụp từ camera"
   - Nhìn thẳng vào camera
   - Nhấn SPACE để chụp
   - Nhấn ESC để hủy
5. Lưu thông tin

### 3. Tạo lớp học

1. **Menu** → **Quản lý** → **Quản lý lớp học**
2. Nhấn **"Tạo lớp mới"**
3. Nhập: Tên lớp, Giảng viên
4. Thêm sinh viên vào lớp

### 4. Điểm danh

1. **Chọn lớp học** từ dropdown
2. **Bắt đầu camera**: Nhấn "Bắt đầu Camera"
3. **Bắt đầu phiên điểm danh**: Toolbar → "Bắt đầu điểm danh"
4. Sinh viên đứng trước camera → **Tự động điểm danh**
5. Theo dõi danh sách điểm danh bên phải
6. **Kết thúc**: Toolbar → "Kết thúc điểm danh"

### 5. Xem báo cáo

1. **Menu** → **Tệp** → **Xuất báo cáo**
2. Chọn loại báo cáo:
   - Báo cáo theo ngày
   - Báo cáo theo tuần
   - Báo cáo theo tháng
   - Báo cáo sinh viên
3. Chọn định dạng: Excel hoặc PDF
4. Lưu file báo cáo

## Tính năng chính

### 🎯 Nhận diện khuôn mặt
- **Thuật toán**: face_recognition + dlib
- **Độ chính xác**: 95%+ trong điều kiện ánh sáng tốt
- **Tốc độ**: Real-time (~30 FPS)
- **Ngưỡng nhận diện**: Có thể điều chỉnh (0.1-1.0)

### 📊 Quản lý dữ liệu
- **Database**: SQL Server với thiết kế tối ưu
- **Backup**: Tự động backup encodings
- **Import/Export**: Hỗ trợ nhiều định dạng
- **Validation**: Kiểm tra tính hợp lệ dữ liệu

### 📈 Báo cáo chi tiết
- **Excel**: Với formatting và charts
- **PDF**: Layout chuyên nghiệp
- **CSV**: Cho data analysis
- **Thống kê**: Tỷ lệ điểm danh, top students, etc.

### 🔧 Tùy chỉnh linh hoạt
- **Cấu hình**: File config.py dễ chỉnh sửa
- **Themes**: Hỗ trợ nhiều giao diện
- **Languages**: Tiếng Việt/English
- **Camera**: Hỗ trợ nhiều camera

## Troubleshooting

### Lỗi thường gặp

1. **"Không thể kết nối database"**
   ```
   ✅ Kiểm tra SQL Server đang chạy
   ✅ Kiểm tra tên server trong config.py
   ✅ Kiểm tra quyền truy cập database
   ```

2. **"Camera không hoạt động"**
   ```
   ✅ Kiểm tra camera đã được kết nối
   ✅ Tắt các ứng dụng khác đang dùng camera
   ✅ Thử thay đổi camera index (0, 1, 2...)
   ```

3. **"Không nhận diện được khuôn mặt"**
   ```
   ✅ Kiểm tra ánh sáng đủ sáng
   ✅ Khuôn mặt nhìn thẳng camera
   ✅ Điều chỉnh ngưỡng tolerance
   ✅ Thử train lại với ảnh chất lượng cao
   ```

4. **"Lỗi import face_recognition"**
   ```
   ✅ Cài đặt Visual C++ Redistributable
   ✅ Cài cmake: pip install cmake
   ✅ Cài dlib: pip install dlib
   ✅ Cài face_recognition: pip install face_recognition
   ```

### Performance tuning

1. **Tăng tốc độ nhận diện**:
   ```python
   # Trong config.py
   PERFORMANCE_CONFIG = {
       'process_every_nth_frame': 3,  # Xử lý mỗi frame thứ 3
       'resize_factor': 0.25,         # Giảm kích thước frame
   }
   ```

2. **Giảm sử dụng RAM**:
   ```python
   PERFORMANCE_CONFIG = {
       'cache_encodings': False,      # Tắt cache
       'face_recognition_workers': 1, # Giảm workers
   }
   ```

### Backup và phục hồi

1. **Backup encodings**:
   ```bash
   # Tự động backup trong thư mục data/
   # Hoặc manual backup
   python -c "from face_recognition.face_encoder import FaceEncoder; FaceEncoder().backup_encodings()"
   ```

2. **Backup database**:
   ```sql
   -- Trong SQL Server Management Studio
   -- Right click database → Tasks → Back Up...
   ```

## API Documentation

### Database API

```python
from database.db import db_manager

# Thêm user
db_manager.add_user("Nguyễn Văn A", "SV001", "Student")

# Lấy attendance records
records = db_manager.get_attendance_records(class_id=1, date_from="2024-01-01")
```

### Face Recognition API

```python
from face_recognition.recognizer import FaceRecognizer

recognizer = FaceRecognizer()

# Thêm khuôn mặt
recognizer.add_known_face(user_id=1, name="John", student_id="SV001", image_path="face.jpg")

# Nhận diện
results = recognizer.recognize_faces(camera_frame)
```

### Report API

```python
from reports.report_generator import report_generator

# Tạo báo cáo daily
report_path = report_generator.generate_daily_attendance_report(
    report_date="2024-01-15", 
    class_id=1, 
    format='excel'
)
```

## Đóng góp

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Liên hệ

- **Email**: your-email@example.com
- **GitHub**: https://github.com/yourusername/face-attendance-system
- **Issues**: https://github.com/yourusername/face-attendance-system/issues

## Changelog

### v1.0.0 (2024-01-01)
- ✅ Phiên bản đầu tiên
- ✅ Face recognition cơ bản
- ✅ Database integration
- ✅ GUI với PyQt5
- ✅ Report generation
- ✅ Logging system

### Tính năng sắp tới
- 🔄 Multi-camera support
- 🔄 Cloud database option  
- 🔄 Mobile app
- 🔄 Advanced analytics
- 🔄 Integration với LMS