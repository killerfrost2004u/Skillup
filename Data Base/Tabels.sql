CREATE DATABASE skill_up
GO

-- ==========================
-- ???? ?????????? (Users)
-- ==========================
CREATE TABLE Users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) UNIQUE NOT NULL,
    password NVARCHAR(100) NOT NULL,
    role NVARCHAR(50) CHECK (role IN ('student', 'instructor', 'admin')) NOT NULL,
    profile_image NVARCHAR(MAX) NULL,
    age INT NULL,
    year NVARCHAR(50) NULL,
    major NVARCHAR(100) NULL,
    college NVARCHAR(100) NULL
);
GO


-- ==========================
-- ???? ???????? (Courses)
-- ==========================


CREATE TABLE Courses (
    course_id INT IDENTITY(1,1) PRIMARY KEY,
    course_name NVARCHAR(200) NOT NULL,
    track_name NVARCHAR(200) NULL
);
GO


-- . جدول التراكات
CREATE TABLE Tracks (
    track_id INT IDENTITY(1,1) PRIMARY KEY,
    track_name NVARCHAR(200) NOT NULL UNIQUE
);
GO

-- . جدول الربط بين التراكات والكورسات
CREATE TABLE TrackCourses (
    id INT IDENTITY(1,1) PRIMARY KEY,
    track_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
GO


CREATE TABLE Lectures (
    lecture_id INT IDENTITY(1,1) PRIMARY KEY,
    course_id INT NOT NULL,
    lecture_name NVARCHAR(200) NULL,  
    youtube_link NVARCHAR(MAX) NOT NULL,  
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE StudentLectureProgress (
    id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    progress_percent INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

GO
