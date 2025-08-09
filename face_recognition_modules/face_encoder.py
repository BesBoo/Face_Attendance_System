import pickle
import numpy as np
import os
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

class FaceEncoder:
    def __init__(self, encodings_file_path: str = "data/encodings.pkl"):
        self.encodings_file_path = encodings_file_path
        self.known_encodings = {}  
        self.user_names = {}       
        self.user_student_ids = {} 

        os.makedirs(os.path.dirname(encodings_file_path), exist_ok=True)
        

        self.load_encodings()
    
    def add_encoding(self, user_id: int, name: str, student_id: str, encoding: np.ndarray) -> bool:
        """
        Thêm face encoding mới cho user
        """
        try:
            self.known_encodings[user_id] = encoding
            self.user_names[user_id] = name
            self.user_student_ids[user_id] = student_id
            
            success = self.save_encodings()
            
            if success:
                logging.info(f"Đã thêm face encoding cho user: {name} (ID: {user_id})")
            
            return success
            
        except Exception as e:
            logging.error(f"Lỗi thêm face encoding: {e}")
            return False
    
    def update_encoding(self, user_id: int, name: str = None, student_id: str = None, 
                       encoding: np.ndarray = None) -> bool:
        """
        Cập nhật face encoding hoặc thông tin user
        """
        try:
            if user_id not in self.known_encodings:
                logging.warning(f"User ID {user_id} không tồn tại trong encodings")
                return False
            
            if name:
                self.user_names[user_id] = name
            if student_id:
                self.user_student_ids[user_id] = student_id
            if encoding is not None:
                self.known_encodings[user_id] = encoding
            
            success = self.save_encodings()
            
            if success:
                logging.info(f"Đã cập nhật thông tin cho user ID: {user_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Lỗi cập nhật face encoding: {e}")
            return False
    
    def remove_encoding(self, user_id: int) -> bool:
        """
        Xóa face encoding của user
        """
        try:
            if user_id in self.known_encodings:
                del self.known_encodings[user_id]
                del self.user_names[user_id]
                del self.user_student_ids[user_id]
                
                success = self.save_encodings()
                
                if success:
                    logging.info(f"Đã xóa face encoding cho user ID: {user_id}")
                
                return success
            else:
                logging.warning(f"User ID {user_id} không tồn tại")
                return True
                
        except Exception as e:
            logging.error(f"Lỗi xóa face encoding: {e}")
            return False
    
    def get_all_encodings(self) -> Tuple[List[np.ndarray], List[int], List[str]]:
        """
        Lấy tất cả encodings, user IDs và tên
        Returns: (encodings, user_ids, names)
        """
        encodings = []
        user_ids = []
        names = []
        
        for user_id, encoding in self.known_encodings.items():
            encodings.append(encoding)
            user_ids.append(user_id)
            names.append(self.user_names.get(user_id, f"User_{user_id}"))
        
        return encodings, user_ids, names
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """
        Lấy thông tin user theo ID
        """
        if user_id in self.known_encodings:
            return {
                'user_id': user_id,
                'name': self.user_names.get(user_id, ''),
                'student_id': self.user_student_ids.get(user_id, ''),
                'has_encoding': True
            }
        return None
    
    def save_encodings(self) -> bool:
        """
        Lưu encodings vào file pickle
        """
        try:
            data = {
                'encodings': self.known_encodings,
                'names': self.user_names,
                'student_ids': self.user_student_ids,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.encodings_file_path, 'wb') as f:
                pickle.dump(data, f)
            
            logging.info(f"Đã lưu {len(self.known_encodings)} encodings vào {self.encodings_file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Lỗi lưu encodings: {e}")
            return False
    
    def load_encodings(self) -> bool:
        """
        Load encodings từ file pickle
        """
        try:
            if not os.path.exists(self.encodings_file_path):
                logging.info("File encodings chưa tồn tại, khởi tạo mới")
                return True
            
            with open(self.encodings_file_path, 'rb') as f:
                data = pickle.load(f)
            

            if isinstance(data, dict):
                self.known_encodings = data.get('encodings', {})
                self.user_names = data.get('names', {})
                self.user_student_ids = data.get('student_ids', {})
            else:

                logging.warning("Định dạng file encodings cũ, đang chuyển đổi...")
                self.known_encodings = data if isinstance(data, dict) else {}
                self.user_names = {}
                self.user_student_ids = {}
            
            logging.info(f"Đã load {len(self.known_encodings)} encodings từ {self.encodings_file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Lỗi load encodings: {e}")
 
            self.known_encodings = {}
            self.user_names = {}
            self.user_student_ids = {}
            return False
    
    def backup_encodings(self, backup_path: str = None) -> bool:
        """
        Tạo backup của encodings
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/encodings_backup_{timestamp}.pkl"
            

            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            data = {
                'encodings': self.known_encodings,
                'names': self.user_names,
                'student_ids': self.user_student_ids,
                'backup_time': datetime.now().isoformat(),
                'original_file': self.encodings_file_path
            }
            
            with open(backup_path, 'wb') as f:
                pickle.dump(data, f)
            
            logging.info(f"Đã backup encodings vào {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"Lỗi backup encodings: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore encodings từ backup
        """
        try:
            if not os.path.exists(backup_path):
                logging.error(f"File backup không tồn tại: {backup_path}")
                return False
            
            with open(backup_path, 'rb') as f:
                data = pickle.load(f)
            
            self.known_encodings = data.get('encodings', {})
            self.user_names = data.get('names', {})
            self.user_student_ids = data.get('student_ids', {})
            
            success = self.save_encodings()
            
            if success:
                logging.info(f"Đã restore {len(self.known_encodings)} encodings từ {backup_path}")
            
            return success
            
        except Exception as e:
            logging.error(f"Lỗi restore encodings: {e}")
            return False
    
    def get_encoding_stats(self) -> Dict:
        """
        Lấy thống kê về encodings
        """
        return {
            'total_users': len(self.known_encodings),
            'file_path': self.encodings_file_path,
            'file_exists': os.path.exists(self.encodings_file_path),
            'file_size': os.path.getsize(self.encodings_file_path) if os.path.exists(self.encodings_file_path) else 0,
            'users_with_names': len([uid for uid in self.known_encodings.keys() if uid in self.user_names]),
            'users_with_student_ids': len([uid for uid in self.known_encodings.keys() if uid in self.user_student_ids])
        }
    
    def validate_encodings(self) -> List[str]:
        """
        Kiểm tra tính hợp lệ của encodings
        Returns: List các lỗi tìm thấy
        """
        errors = []
        
        try:
            for user_id, encoding in self.known_encodings.items():
                if not isinstance(encoding, np.ndarray):
                    errors.append(f"User ID {user_id}: Encoding không phải numpy array")
                elif encoding.shape != (128,):
                    errors.append(f"User ID {user_id}: Encoding shape không đúng {encoding.shape}, cần (128,)")
                elif np.isnan(encoding).any():
                    errors.append(f"User ID {user_id}: Encoding chứa giá trị NaN")
                elif np.isinf(encoding).any():
                    errors.append(f"User ID {user_id}: Encoding chứa giá trị vô cực")
                
                if user_id not in self.user_names:
                    errors.append(f"User ID {user_id}: Thiếu tên")
                if user_id not in self.user_student_ids:
                    errors.append(f"User ID {user_id}: Thiếu student ID")
        
        except Exception as e:
            errors.append(f"Lỗi kiểm tra encodings: {e}")
        
        return errors
    
    def clear_all_encodings(self) -> bool:
        """
        Xóa tất cả encodings (cẩn thần!)
        """
        try:
            self.known_encodings.clear()
            self.user_names.clear()
            self.user_student_ids.clear()
            
            success = self.save_encodings()
            
            if success:
                logging.warning("Đã xóa tất cả face encodings")
            
            return success
            
        except Exception as e:
            logging.error(f"Lỗi xóa tất cả encodings: {e}")
            return False