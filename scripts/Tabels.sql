=========================
  --انشاء قاعدة بيانات
=========================
CREATE DATABASE elearning_platform
- ========================================
-- جدول المستخدمين (Users)
-- ========================================
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) UNIQUE NOT NULL,
    password NVARCHAR(100) NOT NULL,
    role NVARCHAR(50) CHECK (role IN ('student', 'instructor', 'admin')) NOT NULL
);
GO

-- ========================================
-- جدول الكورسات (Courses)
-- ========================================
CREATE TABLE Courses (
    course_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    instructor_id INT NOT NULL,
    price DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (instructor_id) REFERENCES Users(user_id)
);
GO

-- ========================================
-- جدول الدروس (Lessons)
-- ========================================
CREATE TABLE Lessons (
    lesson_id INT IDENTITY(1,1) PRIMARY KEY,
    course_id INT NOT NULL,
    title NVARCHAR(200) NOT NULL,
    content NVARCHAR(MAX),
    position INT,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
GO

-- ========================================
-- جدول الاشتراكات (Enrollments)
-- ========================================
CREATE TABLE Enrollments (
    enrollment_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    date_enrolled DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
GO

-- ========================================
-- جدول المدفوعات (Payments)
-- ========================================
CREATE TABLE Payments (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method NVARCHAR(50),
    status NVARCHAR(50) CHECK (status IN ('pending', 'completed', 'failed')) DEFAULT 'pending',
    date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
GO

-- ========================================
-- جدول التقييمات (Reviews)
-- ========================================
CREATE TABLE Reviews (
    review_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
GO
