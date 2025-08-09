# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from gui.main_window import AttendanceMainWindow
from utils.logger import app_logger, log_system_event
from utils.helpers import ensure_directory_exists

class SplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        
        title_font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter | Qt.AlignTop, 
                        "\nHỆ THỐNG ĐIỂM DANH\nBẰNG KHUÔN MẶT")
        
        info_font = QFont("Arial", 10)
        painter.setFont(info_font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, 
                        "\n\n\n\nĐang khởi động...\n\nPhiên bản 1.0\nSử dụng Python + OpenCV + PyQt5")
        
        painter.end()
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)

def check_dependencies():
    """Kiểm tra các thư viện cần thiết"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import face_recognition
    except ImportError:
        missing_deps.append("face_recognition")
    
    try:
        import pyodbc
    except ImportError:
        missing_deps.append("pyodbc")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import xlsxwriter
    except ImportError:
        missing_deps.append("xlsxwriter")
    
    try:
        import reportlab
    except ImportError:
        missing_deps.append("reportlab")
    
    if missing_deps:
        error_msg = "Thiếu các thư viện sau:\n" + "\n".join(missing_deps)
        error_msg += "\n\nVui lòng cài đặt bằng lệnh:\npip install " + " ".join(missing_deps)
        return False, error_msg
    
    return True, ""

def setup_directories():
    """Tạo các thư mục cần thiết"""
    directories = [
        "data",
        "data/images",
        "logs",
        "reports"
    ]
    
    for directory in directories:
        ensure_directory_exists(directory)

def main():
    """Hàm chính khởi động ứng dụng"""
    
    app = QApplication(sys.argv)
    app.setApplicationName("Face Attendance System")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Your Organization")
    
    deps_ok, deps_error = check_dependencies()
    if not deps_ok:
        QMessageBox.critical(None, "Lỗi Dependencies", deps_error)
        return 1
    
    splash = SplashScreen()
    splash.show()
    app.processEvents()
    
    try:
        splash.showMessage("Đang tạo thư mục...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        setup_directories()
        
        splash.showMessage("Đang khởi tạo logging...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        log_system_event("STARTUP", "Bắt đầu khởi động ứng dụng")
        
        splash.showMessage("Đang tạo giao diện chính...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        main_window = AttendanceMainWindow()
        
        splash.showMessage("Đang kiểm tra kết nối database...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        splash.showMessage("Đang kiểm tra camera...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        splash.showMessage("Hoàn tất khởi tạo...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        QTimer.singleShot(2000, splash.close) 
        QTimer.singleShot(2000, main_window.show)
        
        log_system_event("STARTUP", "Ứng dụng đã khởi động thành công")
        
        return app.exec_()
        
    except Exception as e:
        splash.close()
        error_msg = f"Lỗi khởi động ứng dụng:\n{str(e)}"
        log_system_event("ERROR", f"Startup error: {e}")
        QMessageBox.critical(None, "Lỗi khởi động", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())