import pyodbc
import logging
from typing import Optional, List, Dict, Any

class DatabaseManager:
    def __init__(self):
        self.server = r'DUCCKY\SQLEXPRESS'
        self.database = 'face_attendance'
        self.connection_string = f'DRIVER={{SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'
        self.connection = None
        
    def connect(self) -> bool:
        """Kết nối đến database"""
        try:
            self.connection = pyodbc.connect(self.connection_string)
            logging.info("Kết nối database thành công")
            return True
        except Exception as e:
            logging.error(f"Lỗi kết nối database: {e}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối database"""
        if self.connection:
            self.connection.close()
            logging.info("Đã ngắt kết nối database")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Thực hiện query SELECT và trả về kết quả"""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            cursor.close()
            return result
            
        except Exception as e:
            logging.error(f"Lỗi thực hiện query: {e}")
            return None
    
    def execute_non_query(self, query: str, params: tuple = None) -> bool:
        """Thực hiện query INSERT, UPDATE, DELETE"""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logging.error(f"Lỗi thực hiện non-query: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_last_insert_id(self) -> Optional[int]:
        """Lấy ID của record vừa được insert"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT @@IDENTITY")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Lỗi lấy last insert ID: {e}")
            return None
    
    def add_user(self, name: str, student_id: str, role: str, image_path: str = None) -> bool:
        """Thêm người dùng mới"""
        query = """
        INSERT INTO users (name, student_id, role, image_path) 
        VALUES (?, ?, ?, ?)
        """
        return self.execute_non_query(query, (name, student_id, role, image_path))
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Lấy thông tin user theo ID"""
        query = "SELECT * FROM users WHERE id = ? AND is_active = 1"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_user_by_student_id(self, student_id: str) -> Optional[Dict]:
        """Lấy thông tin user theo student_id"""
        query = "SELECT * FROM users WHERE student_id = ? AND is_active = 1"
        result = self.execute_query(query, (student_id,))
        return result[0] if result else None
    
    def get_all_users(self, role: str = None) -> List[Dict]:
        """Lấy danh sách tất cả user, có thể filter theo role"""
        if role:
            query = "SELECT * FROM users WHERE role = ? AND is_active = 1 ORDER BY name"
            return self.execute_query(query, (role,)) or []
        else:
            query = "SELECT * FROM users WHERE is_active = 1 ORDER BY name"
            return self.execute_query(query) or []
    
    def update_user(self, user_id: int, name: str = None, student_id: str = None, 
                   role: str = None, image_path: str = None) -> bool:
        """Cập nhật thông tin user"""
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if student_id:
            updates.append("student_id = ?")
            params.append(student_id)
        if role:
            updates.append("role = ?")
            params.append(role)
        if image_path:
            updates.append("image_path = ?")
            params.append(image_path)
        
        if not updates:
            return True
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        return self.execute_non_query(query, tuple(params))
    
    def add_class(self, class_name: str, instructor_name: str, instructor_id: int) -> bool:
        """Thêm lớp học mới"""
        query = """
        INSERT INTO classes (class_name, instructor_name, instructor_id) 
        VALUES (?, ?, ?)
        """
        return self.execute_non_query(query, (class_name, instructor_name, instructor_id))
    
    def get_all_classes(self) -> List[Dict]:
        """Lấy danh sách tất cả lớp học"""
        query = """
        SELECT c.*, u.name as instructor_name_full 
        FROM classes c 
        LEFT JOIN users u ON c.instructor_id = u.id 
        WHERE c.is_active = 1 
        ORDER BY c.class_name
        """
        return self.execute_query(query) or []
    
    def get_class_by_id(self, class_id: int) -> Optional[Dict]:
        """Lấy thông tin lớp học theo ID"""
        query = "SELECT * FROM classes WHERE id = ? AND is_active = 1"
        result = self.execute_query(query, (class_id,))
        return result[0] if result else None
    
    def enroll_student(self, class_id: int, student_id: int) -> bool:
        """Đăng ký sinh viên vào lớp"""
        query = """
        INSERT INTO enrollments (class_id, student_id) 
        VALUES (?, ?)
        """
        return self.execute_non_query(query, (class_id, student_id))
    
    def get_students_in_class(self, class_id: int) -> List[Dict]:
        """Lấy danh sách sinh viên trong lớp"""
        query = """
        SELECT u.*, e.enrolled_at 
        FROM users u 
        INNER JOIN enrollments e ON u.id = e.student_id 
        WHERE e.class_id = ? AND e.is_active = 1 AND u.is_active = 1 
        ORDER BY u.name
        """
        return self.execute_query(query, (class_id,)) or []
    
    def get_classes_for_student(self, student_id: int) -> List[Dict]:
        """Lấy danh sách lớp của sinh viên"""
        query = """
        SELECT c.*, e.enrolled_at 
        FROM classes c 
        INNER JOIN enrollments e ON c.id = e.class_id 
        WHERE e.student_id = ? AND e.is_active = 1 AND c.is_active = 1 
        ORDER BY c.class_name
        """
        return self.execute_query(query, (student_id,)) or []
    
    def add_attendance(self, user_id: int, class_id: int, attendance_date: str, 
                      attendance_time: str, status: str = 'Present') -> bool:
        """Thêm điểm danh"""
        query = """
        INSERT INTO attendance_records (user_id, class_id, attendance_date, attendance_time, status) 
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_non_query(query, (user_id, class_id, attendance_date, attendance_time, status))
    
    def get_attendance_records(self, class_id: int = None, user_id: int = None, 
                             date_from: str = None, date_to: str = None) -> List[Dict]:
        """Lấy bản ghi điểm danh với các filter"""
        conditions = []
        params = []
        
        if class_id:
            conditions.append("a.class_id = ?")
            params.append(class_id)
        if user_id:
            conditions.append("a.user_id = ?")
            params.append(user_id)
        if date_from:
            conditions.append("a.attendance_date >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("a.attendance_date <= ?")
            params.append(date_to)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT a.*, u.name as user_name, u.student_id, c.class_name 
        FROM attendance_records a 
        INNER JOIN users u ON a.user_id = u.id 
        INNER JOIN classes c ON a.class_id = c.id 
        WHERE {where_clause} 
        ORDER BY a.attendance_date DESC, a.attendance_time DESC
        """
        
        return self.execute_query(query, tuple(params)) or []
    
    def check_attendance_exists(self, user_id: int, class_id: int, date: str) -> bool:
        """Kiểm tra xem đã điểm danh chưa"""
        query = """
        SELECT COUNT(*) as count 
        FROM attendance_records 
        WHERE user_id = ? AND class_id = ? AND attendance_date = ?
        """
        result = self.execute_query(query, (user_id, class_id, date))
        return result[0]['count'] > 0 if result else False

db_manager = DatabaseManager()