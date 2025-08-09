import pyodbc
import os

# Kết nối đến SQL Server
server = r'DUCCKY\SQLEXPRESS'  # Đổi thành server của bạn
database = 'face_attendance'  # Tên CSDL bạn đã tạo

connection_string = (
    f'DRIVER={{SQL Server}};'
    f'SERVER={r'DUCCKY\SQLEXPRESS'};'
    f'DATABASE={'face_attendance'};'
    f'Trusted_Connection=yes;'
)

def run_sql_script(file_path):
    try:
        # Kết nối đến database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Đọc nội dung file SQL
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # Tách và thực thi từng câu lệnh SQL
        commands = sql_script.split(';')
        for command in commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                except Exception as e:
                    print(f"❌ Lỗi khi thực thi lệnh:\n{command}\n→ {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print(" Đã chạy file SQL thành công.")

    except Exception as e:
        print(f"❌ Lỗi kết nối hoặc đọc file SQL: {e}")

if __name__ == "__main__":
    sql_file_path = os.path.join("database", "setup_db.sql")
    run_sql_script(sql_file_path)
