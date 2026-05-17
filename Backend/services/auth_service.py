import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24

# ============================================
# 4. DEPENDENCY INJECTION (Service Layer)
# ============================================
class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def register_user(self, username, email, password, role="student"):
        existing = self.user_repo.get_by_email(email)
        if existing:
            return {"error": "Email already exists", "status": 400}

        hashed_password = generate_password_hash(password)
        success = self.user_repo.create(username, email, hashed_password, role)
        
        if success:
            return {"message": "Registration successful", "status": 201}
        return {"error": "Failed to register user", "status": 500}

    def login_user(self, identity, password):
        user = self.user_repo.get_by_identity(identity)
        if not user:
            return {"error": "Invalid username or password", "status": 401}

        password_correct = False
        db_password = user['password']

        if db_password.startswith(('pbkdf2:sha256', 'scrypt:')):
            if check_password_hash(db_password, password):
                password_correct = True
        elif db_password == password:
            password_correct = True
            new_hash = generate_password_hash(password)
            self.user_repo.update_password(user['user_id'], new_hash)

        if not password_correct:
            return {"error": "Invalid username or password", "status": 401}

        token = self._generate_token(user)
        
        profile = {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "profile_image": user["profile_image"] or "user.jpg",
            "age": user["age"] or 20,
            "year": user["year"] or "Year",
            "major": user["major"] or "Computer",
            "college": user["college"] or "College",
            "token": token,
            "message": "Login successful"
        }
        return {"data": profile, "status": 200}

    def validate_token(self, token):
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user = self.user_repo.get_by_id(data['user_id'])
            return user
        except:
            return None

    def _generate_token(self, user):
        token_data = {
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        return jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
