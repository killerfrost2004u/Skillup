import unittest
from unittest.mock import Mock
from Backend.services.course_service import CourseService, ProgressObserver

class MockObserver(ProgressObserver):
    def __init__(self):
        self.notified = False
        self.last_percent = 0

    def update(self, user_id, playlist_id, percent):
        self.notified = True
        self.last_percent = percent

class TestCourseService(unittest.TestCase):
    def setUp(self):
        self.mock_course_repo = Mock()
        self.course_service = CourseService(self.mock_course_repo)

    def test_get_all_courses(self):
        """Verification: Ensures courses are retrieved from the repository."""
        self.mock_course_repo.get_all.return_value = [{"course_id": 1, "name": "Python"}]
        
        courses = self.course_service.get_all_courses()
        
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]["name"], "Python")

    def test_save_progress_notifies_observers(self):
        """Behavioral Pattern: Validates the Observer pattern in action."""
        # 1. Arrange: Attach a mock observer
        observer = MockObserver()
        self.course_service.add_observer(observer)
        
        progress_data = {
            "playlist_id": "python-101",
            "overall_progress": 50,
            "completed_videos": 5,
            "total_videos": 10
        }

        # 2. Act
        self.course_service.save_progress(user_id=1, data=progress_data)

        # 3. Assert
        self.assertTrue(observer.notified)
        self.assertEqual(observer.last_percent, 50)
        self.mock_course_repo.save_playlist_progress.assert_called_once()

    def test_get_playlist_progress_success(self):
        """Verification: Validates complex data aggregation for playlist progress."""
        self.mock_course_repo.get_video_progress.return_value = [
            {"video_id": "v1", "completed": True}
        ]
        self.mock_course_repo.get_playlist_stats.return_value = {
            "overall_progress": 100,
            "completed_videos": 1,
            "total_videos": 1
        }

        result = self.course_service.get_playlist_progress(user_id=1, playlist_id="p1")

        self.assertTrue(result["success"])
        self.assertEqual(result["progress_percentage"], 100)
        self.assertIn("v1", result["videos"])
        self.assertTrue(result["videos"]["v1"]["completed"])

if __name__ == '__main__':
    unittest.main()
