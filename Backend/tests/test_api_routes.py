import unittest
from unittest.mock import Mock
from Backend.app import create_app

class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        
        # Isolation: Mock the services attached to the app
        self.app.auth_service = Mock()
        self.app.course_service = Mock()
        self.app.ai_service = Mock()

    def test_register_route_success(self):
        """Verification: Ensures the /register route correctly passes data to AuthService."""
        # 1. Arrange
        self.app.auth_service.register_user.return_value = {
            "message": "User created",
            "status": 201
        }
        payload = {
            "username": "test",
            "email": "test@test.com",
            "password": "password123"
        }

        # 2. Act
        response = self.client.post('/register', json=payload)

        # 3. Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["message"], "User created")
        self.app.auth_service.register_user.assert_called_once_with(
            "test", "test@test.com", "password123", "student"
        )

    def test_login_route_success(self):
        """Verification: Ensures the /login route returns the profile data on success."""
        # 1. Arrange
        self.app.auth_service.login_user.return_value = {
            "data": {"user_id": 1, "name": "test", "token": "mock-token"},
            "status": 200
        }
        payload = {"username": "test", "password": "password123"}

        # 2. Act
        response = self.client.post('/login', json=payload)

        # 3. Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["token"], "mock-token")

    def test_get_courses_route(self):
        """Verification: Ensures the /courses route returns course data."""
        self.app.course_service.get_all_courses.return_value = [{"id": 1}]
        
        response = self.client.get('/courses')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

if __name__ == '__main__':
    unittest.main()
