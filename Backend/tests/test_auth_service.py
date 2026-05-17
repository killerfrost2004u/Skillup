import unittest
from unittest.mock import Mock, patch
from Backend.services.auth_service import AuthService

class TestAuthService(unittest.TestCase):
    def setUp(self):
        # Isolation: Mocking the repository to test the service in isolation
        self.mock_user_repo = Mock()
        self.auth_service = AuthService(self.mock_user_repo)

    def test_register_user_success(self):
        """Verification: Validates that a user can register with valid details."""
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.create.return_value = True

        result = self.auth_service.register_user("testuser", "test@example.com", "password123")
        
        self.assertEqual(result["status"], 201)
        self.assertEqual(result["message"], "Registration successful")
        self.mock_user_repo.create.assert_called_once()

    def test_register_user_existing_email(self):
        """Validation: Ensures business rules prevent duplicate email registrations."""
        self.mock_user_repo.get_by_email.return_value = {"email": "test@example.com"}

        result = self.auth_service.register_user("testuser", "test@example.com", "password123")
        
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "Email already exists")
        self.mock_user_repo.create.assert_not_called()

    def test_login_user_success(self):
        """Verification: Validates that a user can login with correct credentials."""
        # Mock user data as returned by repository
        from werkzeug.security import generate_password_hash
        hashed_pw = generate_password_hash("password123")
        
        mock_user = {
            "user_id": 1,
            "name": "testuser",
            "email": "test@example.com",
            "password": hashed_pw,
            "role": "student",
            "profile_image": None,
            "age": None,
            "year": None,
            "major": None,
            "college": None
        }
        
        self.mock_user_repo.get_by_identity.return_value = mock_user
        
        result = self.auth_service.login_user("testuser", "password123")
        
        self.assertEqual(result["status"], 200)
        self.assertIn("token", result["data"])
        self.assertEqual(result["data"]["name"], "testuser")

    def test_login_user_invalid_password(self):
        """Validation: Ensures incorrect passwords are rejected."""
        from werkzeug.security import generate_password_hash
        hashed_pw = generate_password_hash("password123")
        
        mock_user = {
            "user_id": 1,
            "password": hashed_pw
        }
        
        self.mock_user_repo.get_by_identity.return_value = mock_user
        
        result = self.auth_service.login_user("testuser", "wrongpassword")
        
        self.assertEqual(result["status"], 401)
        self.assertEqual(result["error"], "Invalid username or password")

if __name__ == '__main__':
    unittest.main()
