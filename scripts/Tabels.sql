INSERT INTO Users (name, email, password, role) VALUES
('Ahmed Ali', 'ahmed@example.com', '12345', 'instructor'),
('Sara Mohamed', 'sara@example.com', '12345', 'student'),
('Omar Khaled', 'omar@example.com', '12345', 'student'),
('Mariam Hassan', 'mariam@example.com', '12345', 'instructor'),
('Admin', 'admin@elearn.com', '12345', 'admin');

INSERT INTO Courses (title, description, instructor_id, price) VALUES
('Python Basics', N'كورس لتعلم أساسيات بايثون', 1, 199.00),
('Web Development', N'مقدمة لتصميم مواقع الويب', 4, 249.00),
('Data Analysis Intro', N'مقدمة في تحليل البيانات', 1, 299.00);

INSERT INTO Lessons (course_id, title, content, position) VALUES
(1, N'مقدمة عن بايثون', N'درس تعريفي بلغة بايثون', 1),
(1, N'أنواع البيانات', N'شرح أنواع البيانات في بايثون', 2),
(2, N'HTML Basics', N'مقدمة عن HTML', 1),
(2, N'CSS Intro', N'تنسيق المواقع بـ CSS', 2),
(3, N'ما هو تحليل البيانات', N'شرح المفهوم الأساسي لتحليل البيانات', 1);

INSERT INTO Enrollments (user_id, course_id, date_enrolled) VALUES
(2, 1, '2025-10-01'),
(3, 1, '2025-10-02'),
(2, 2, '2025-10-03');

INSERT INTO Payments (user_id, course_id, amount, payment_method, status, date) VALUES
(2, 1, 199.00, 'card', 'completed', '2025-10-01'),
(3, 1, 199.00, 'card', 'completed', '2025-10-02'),
(2, 2, 249.00, 'wallet', 'completed', '2025-10-03');

INSERT INTO Reviews (user_id, course_id, rating, comment, created_at) VALUES
(2, 1, 5, N'الكورس ممتاز جدًا 👌', '2025-10-05'),
(3, 1, 4, N'شرح كويس ومبسط', '2025-10-05'),
(2, 2, 5, N'مفيد جدًا', '2025-10-06');
GO