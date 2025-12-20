INSERT INTO Users (name, email, password, role, profile_image, age, year, major, college) VALUES
('Ahmed Ali', 'ahmed@example.com', '12345', 'instructor','user.jpg',20	,'2028',	'Software Engineering',	'Mansoura University'),
('Aya mohamed', 'ayaa13mm@gmail.com', 'aya123', 'student','user.jpg',21	,'2027',	'Computer Engineering',	'misr higher institute for engineering and technology'),
('Omar Khaled', 'omar@example.com', '12345', 'student','user.jpg',22	,'2026',	'Information Systems',	'Alexandria University'),
('Mariam Hassan', 'mariam@example.com', '12345', 'instructor','user.jpg',25,'2021',	'Cyber Security',	'Ain Shams University'),
('dina kamel', 'dina@gmail.com', '12345', 'student','user.jpg',30	,'2015',	'Computer Science',	'cairo university');

INSERT INTO Tracks (track_name)VALUES 
    ('Backend Development'),
    ('Front-End'),
    ('Python Programming'),
    ('Software Development ');

INSERT INTO Courses (course_name, track_name)
VALUES
('PHP', 'Backend Development'),
('Node.js', 'Backend Development'),
('JavaScript', 'Backend Development'),
('Full Stack Development', 'Software Development'),
('Software Testing', 'Software Development'),
('HTML', 'Front-End'),
('CSS', 'Front-End'),
('JavaScript', 'Front-End'),
('Python GUI', 'Python Programming'),
('Python Basics', 'Python Programming'),
('Python Backend', 'Python Programming');

INSERT INTO TrackCourses (track_id, course_id)
VALUES (1,20), (1,21), (1,22);

-- Software Development => Full Stack Development, Software Testing
INSERT INTO TrackCourses (track_id, course_id)
VALUES (2,23), (2,24);

-- Front-End => HTML, CSS, JavaScript
INSERT INTO TrackCourses (track_id, course_id)
VALUES (3,25), (3,26), (3,27);

-- Python Programming => Python GUI, Python Basics, Python Backend
INSERT INTO TrackCourses (track_id, course_id)
VALUES (4,40), (4,41), (4,42);




INSERT INTO Lectures (course_id, lecture_name, youtube_link)
VALUES 
(20, 'PHP Backend Development', 'https://youtube.com/playlist?list=PLDoPjvoNmBAy41u35AqJUrI-H83DObUDq&si=1zdjYt-lNu7Y7p2x'),
(21, 'Node.js Backend Development', 'https://www.youtube.com/playlist?list=PLQtNtS-WfRa8OF9juY3k6WUWayMfDKHK2'),
(22, 'JavaScript Backend Development', 'https://www.youtube.com/playlist?list=PLDoPjvoNmBAx3kiplQR_oeDqLDBUDYwVv'),
(23, 'Full Stack Development', 'https://youtube.com/playlist?list=PLVrN2LRb7eT2B6v1EwsCS28QkkDTZ5LRm&si=OClRWQFCBsEYKtOV'),
(24, 'Software Testing', 'https://youtube.com/playlist?list=PLzNfs-3kBUJllCa8_6pLYDMnIlg6Lfvu4&si=gDioI4PdqHuWdRp3'),
(25, 'HTML', 'https://youtube.com/playlist?list=PLDoPjvoNmBAw_t_XWUFbBX-c9MafPk9ji&si=YbtLD12a_qi2FNZO'),
(26, 'CSS', 'https://youtube.com/playlist?list=PLDoPjvoNmBAzjsz06gkzlSrlev53MGIKe&si=Iel_jt3KMN-e4iHG'),
(27, 'JavaScript Front-End', 'https://www.youtube.com/playlist?list=PLDoPjvoNmBAx3kiplQR_oeDqLDBUDYwVv'),
(40, 'Python GUI', 'https://youtube.com/playlist?list=PLSiLeKadTQ7nLJxpQo1-944miQKlheu-v&si=7qA9RoGA52Yoo50X'),
(41, 'Python Basics', 'https://youtube.com/playlist?list=PLDoPjvoNmBAyE_gei5d18qkfIe-Z8mocs&si=oXW4J8zJQy0yTq7N'),
(42, 'Python Backend', 'https://youtube.com/playlist?list=PLDoPjvoNmBAyE_gei5d18qkfIe-Z8mocs&si=oXW4J8zJQy0yTq7N');


