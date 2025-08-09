USE face_attendance;

IF OBJECT_ID('attendance_records', 'U') IS NOT NULL DROP TABLE attendance_records;
IF OBJECT_ID('enrollments', 'U') IS NOT NULL DROP TABLE enrollments;
IF OBJECT_ID('classes', 'U') IS NOT NULL DROP TABLE classes;
IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    student_id NVARCHAR(50) UNIQUE NOT NULL,
    role NVARCHAR(20) CHECK (role IN ('Admin', 'Teacher', 'Student')) NOT NULL,
    image_path NVARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    is_active BIT DEFAULT 1
);

CREATE TABLE classes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    class_name NVARCHAR(100) NOT NULL,
    instructor_name NVARCHAR(100) NOT NULL,
    instructor_id INT,
    created_at DATETIME DEFAULT GETDATE(),
    is_active BIT DEFAULT 1,
    FOREIGN KEY (instructor_id) REFERENCES users(id)
);

CREATE TABLE enrollments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    class_id INT NOT NULL,
    student_id INT NOT NULL,
    enrolled_at DATETIME DEFAULT GETDATE(),
    is_active BIT DEFAULT 1,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    UNIQUE(class_id, student_id)
);

CREATE TABLE attendance_records (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    class_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    status NVARCHAR(20) CHECK (status IN ('Present', 'Absent', 'Late')) DEFAULT 'Present',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    UNIQUE(user_id, class_id, attendance_date)
);

INSERT INTO users (name, student_id, role) VALUES 
('Admin User', 'ADMIN001', 'Admin'),
('Nguyễn Văn A', 'GV001', 'Teacher'),
('Trần Thị B', 'SV001', 'Student'),
('Lê Văn C', 'SV002', 'Student'),
('Phạm Thị D', 'SV003', 'Student');

INSERT INTO classes (class_name, instructor_name, instructor_id) VALUES 
('Lập trình Python', 'Nguyễn Văn A', 2),
('Trí tuệ nhân tạo', 'Nguyễn Văn A', 2),
('Cơ sở dữ liệu', 'Nguyễn Văn A', 2);

INSERT INTO enrollments (class_id, student_id) VALUES 
(1, 3), (1, 4), (1, 5),
(2, 3), (2, 4),
(3, 4), (3, 5);

PRINT 'Database setup completed successfully!';