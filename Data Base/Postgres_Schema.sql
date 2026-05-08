-- ==========================
-- Users Table
-- ==========================
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('student', 'instructor', 'admin')) NOT NULL,
    profile_image TEXT NULL,
    age INT NULL,
    year VARCHAR(50) NULL,
    major VARCHAR(100) NULL,
    college VARCHAR(100) NULL
);

-- ==========================
-- Tracks Table
-- ==========================
CREATE TABLE Tracks (
    track_id SERIAL PRIMARY KEY,
    track_name VARCHAR(200) NOT NULL UNIQUE
);

-- ==========================
-- Courses Table
-- ==========================
CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(200) NOT NULL,
    track_name VARCHAR(200) NULL
);

-- ==========================
-- TrackCourses Table (Link)
-- ==========================
CREATE TABLE TrackCourses (
    id SERIAL PRIMARY KEY,
    track_id INT NOT NULL,
    course_id INT NOT NULL,
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
);

-- ==========================
-- Lectures Table
-- ==========================
CREATE TABLE Lectures (
    lecture_id SERIAL PRIMARY KEY,
    course_id INT NOT NULL,
    lecture_name VARCHAR(200) NULL,  
    youtube_link TEXT NOT NULL,  
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
);

-- ==========================
-- UserProgress (Video Status)
-- ==========================
CREATE TABLE VideoProgress (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    playlist_id VARCHAR(200) NOT NULL,
    video_id VARCHAR(200) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, playlist_id, video_id)
);

-- ==========================
-- PlaylistProgress (Overall)
-- ==========================
CREATE TABLE PlaylistProgress (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    playlist_id VARCHAR(200) NOT NULL,
    overall_progress INT DEFAULT 0,
    completed_videos INT DEFAULT 0,
    total_videos INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(user_id, playlist_id)
);
