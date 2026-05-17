import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import logging
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ============================================
# 1. DATABASE CONFIGURATION
# ============================================
DATABASE_URL = os.getenv('DATABASE_URL')
# Robust check for Vercel environment
IS_VERCEL = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None
IS_LOCAL = not IS_VERCEL
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24

def get_db_connection():
    """Get database connection (PostgreSQL for Vercel, SQLite for Local)"""
    try:
        # If we have DATABASE_URL (Neon PostgreSQL), prioritize it
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        else:
            # Fallback to local SQLite
            # Use absolute path for robustness
            base_dir = os.path.dirname(os.path.abspath(__file__))
            sqlite_db_path = os.path.join(base_dir, 'skill_up.db')
            
            # If we are in the 'Backend' directory, the above works.
            # If we are called from 'api/index.py', we might need to adjust.
            if not os.path.exists(sqlite_db_path):
                # Try one level up if not found (for when called from api/)
                sqlite_db_path = os.path.join(os.path.dirname(base_dir), 'Backend', 'skill_up.db')

            conn = sqlite3.connect(sqlite_db_path)
            conn.row_factory = sqlite3.Row # To match RealDictCursor behavior
            return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None

# ============================================
# 2. DATABASE HELPER FUNCTIONS
# ============================================
def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    """Execute SQL query and return results"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        is_sqlite = isinstance(conn, sqlite3.Connection)
        if is_sqlite:
            # SQLite uses ? for placeholders instead of %s
            query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(query, params)
        else:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
        if fetch_one:
            row = cursor.fetchone()
            if is_sqlite and row:
                return dict(row)
            return row
        elif fetch_all:
            rows = cursor.fetchall()
            if is_sqlite:
                return [dict(row) for row in rows]
            return rows
        else:
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"❌ Query error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_by_identity(identity):
    """Get user by username or email (case-insensitive)"""
    return execute_query(
        "SELECT user_id, name, email, password, role, profile_image, age, year, major, college FROM Users WHERE LOWER(name)=LOWER(%s) OR LOWER(email)=LOWER(%s)",
        (identity, identity),
        fetch_one=True
    )

# ============================================
# AUTHENTICATION MIDDLEWARE
# ============================================
def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = execute_query(
                "SELECT user_id, name, email, role FROM Users WHERE user_id=%s",
                (data['user_id'],),
                fetch_one=True
            )
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            request.current_user = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated

# ============================================
# 3. ROUTES
# ============================================

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "student")

        if not all([username, email, password]):
            return jsonify({"message": "Missing required fields"}), 400

        existing = execute_query("SELECT * FROM Users WHERE LOWER(email)=LOWER(%s)", (email,), fetch_one=True)
        if existing:
            return jsonify({"message": "Email already exists"}), 400

        hashed_password = generate_password_hash(password)
        success = execute_query(
            "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, role)
        )

        if success:
            return jsonify({"message": "Registration successful"}), 201
        else:
            return jsonify({"message": "Failed to register user"}), 500
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = get_user_by_identity(username)

        if not user:
            return jsonify({"message": "Invalid username or password"}), 401

        # Check password (supports migration from plain-text)
        password_correct = False
        db_password = user['password']

        # 1. Try secure hash check
        if db_password.startswith('pbkdf2:sha256') or db_password.startswith('scrypt:'):
            if check_password_hash(db_password, password):
                password_correct = True
        # 2. Fallback to plain-text (and migrate)
        elif db_password == password:
            password_correct = True
            # Upgrade user to secure hash automatically
            new_hash = generate_password_hash(password)
            execute_query("UPDATE Users SET password=%s WHERE user_id=%s", (new_hash, user['user_id']))
            logger.info(f"✅ User {user['user_id']} migrated to secure password hash.")

        if password_correct:
            token_data = {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            }
            token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

            return jsonify({
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
            }), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"message": "Internal server error"}), 500

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    try:
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'authenticated': False}), 200

        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = execute_query(
            "SELECT user_id, name, email, role FROM Users WHERE user_id=%s",
            (data['user_id'],),
            fetch_one=True
        )

        if user:
            return jsonify({'authenticated': True, 'user': user}), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        return jsonify({'authenticated': False}), 200

@app.route('/update-profile', methods=['POST'])
def update_profile():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        profile_image = data.get('profile_image')
        age = data.get('age')
        year = data.get('year')
        major = data.get('major')
        college = data.get('college')

        success = execute_query(
            "UPDATE Users SET name=%s, profile_image=%s, age=%s, year=%s, major=%s, college=%s WHERE email=%s",
            (name, profile_image, age, year, major, college, email)
        )

        if success:
            return jsonify({"message": "Profile updated successfully"}), 200
        else:
            return jsonify({"message": "Failed to update profile"}), 500
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({"message": "Internal server error"}), 500

# -------------------------------
# CHAT WITH LOCAL AI (RESTRICTED)
# -------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot messages. Restricted to localhost/local development."""
    # Strict check: only allow if NOT on Vercel
    if not IS_LOCAL:
        return jsonify({
            'reply': 'عذراً، نظام الدردشة متاح فقط عند تشغيل المشروع محلياً لتوفير التكاليف.',
            'error': 'Chat restricted to localhost'
        }), 403

    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'reply': 'Please send a message.'}), 400

        # Option 1: Try OpenAI if key is available in .env (for local use)
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful e-learning assistant for SkillUp platform."},
                        {"role": "user", "content": user_message}
                    ]
                )
                return jsonify({'reply': response.choices[0].message.content})
            except Exception as e:
                logger.error(f"OpenAI error: {e}")

        # Option 2: Local Ollama (Fallback for local)
        system_instruction = "You are a helpful e-learning assistant for an educational platform. Help students with programming courses like Python, Web Development, and other technical subjects. Respond accurately and politely. If the user speaks Arabic, respond in Arabic."
        prompt_text = f"System: {system_instruction}\n\nUser: {user_message}\nAssistant:"

        ollama_url = "http://localhost:11434/api/generate"
        ollama_payload = {
            "model": "llama3.2",
            "prompt": prompt_text,
            "stream": False
        }

        try:
            response = requests.post(ollama_url, json=ollama_payload, timeout=30)
            if response.status_code == 200:
                bot_reply = response.json().get('response', '')
                return jsonify({
                    'reply': bot_reply,
                    'timestamp': datetime.now().isoformat()
                })
        except requests.exceptions.ConnectionError:
            return jsonify({
                'reply': 'عذراً، نظام الدردشة يتطلب تشغيل Ollama محلياً.',
                'error': 'Ollama not found'
            }), 503

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'reply': 'عذراً، حدث خطأ في نظام الدردشة.',
            'error': str(e)
        }), 500

@app.route('/courses', methods=['GET'])
def get_courses():
    courses = execute_query("SELECT * FROM Courses", fetch_all=True)
    return jsonify(courses or []), 200

@app.route('/get-progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    progress = execute_query(
        "SELECT playlist_id, overall_progress as progress, completed_videos, total_videos FROM PlaylistProgress WHERE user_id=%s",
        (user_id,),
        fetch_all=True
    )
    if progress:
        return jsonify([{"course_name": p['playlist_id'], "progress": p['progress']} for p in progress]), 200
    return jsonify([]), 200

@app.route('/api/progress/save', methods=['POST'])
def save_video_progress():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        playlist_id = data.get('playlist_id')
        video_id = data.get('video_id')
        completed = data.get('completed', False)
        
        overall_progress = data.get('overall_progress')
        completed_videos = data.get('completed_videos')
        total_videos = data.get('total_videos')

        if video_id:
            execute_query(
                "INSERT INTO VideoProgress (user_id, playlist_id, video_id, completed) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (user_id, playlist_id, video_id) DO UPDATE SET completed=EXCLUDED.completed, updated_at=CURRENT_TIMESTAMP",
                (user_id, playlist_id, video_id, completed)
            )

        if overall_progress is not None:
            execute_query(
                "INSERT INTO PlaylistProgress (user_id, playlist_id, overall_progress, completed_videos, total_videos) VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (user_id, playlist_id) DO UPDATE SET overall_progress=EXCLUDED.overall_progress, "
                "completed_videos=EXCLUDED.completed_videos, total_videos=EXCLUDED.total_videos, last_updated=CURRENT_TIMESTAMP",
                (user_id, playlist_id, overall_progress, completed_videos, total_videos)
            )

        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"Save progress error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/progress/<int:user_id>/<string:playlist_id>', methods=['GET'])
def get_user_playlist_progress(user_id, playlist_id):
    try:
        videos_progress = execute_query(
            "SELECT video_id, completed FROM VideoProgress WHERE user_id=%s AND playlist_id=%s",
            (user_id, playlist_id),
            fetch_all=True
        )
        
        videos_dict = {v['video_id']: {'completed': v['completed']} for v in videos_progress} if videos_progress else {}
        
        playlist_stats = execute_query(
            "SELECT overall_progress, completed_videos, total_videos FROM PlaylistProgress WHERE user_id=%s AND playlist_id=%s",
            (user_id, playlist_id),
            fetch_one=True
        )

        return jsonify({
            "success": True,
            "user_id": user_id,
            "playlist_id": playlist_id,
            "completed_videos": playlist_stats['completed_videos'] if playlist_stats else 0,
            "total_videos": playlist_stats['total_videos'] if playlist_stats else 0,
            "progress_percentage": playlist_stats['overall_progress'] if playlist_stats else 0,
            "videos": videos_dict
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/check-video-access/<string:playlist_id>', methods=['GET'])
@token_required
def check_video_access(playlist_id):
    return jsonify({"has_access": True, "user_id": request.current_user['user_id'], "playlist_id": playlist_id, "message": "Access granted"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "environment": "Vercel" if IS_VERCEL else "Local",
        "database": "PostgreSQL" if DATABASE_URL else "SQLite",
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == "__main__":
    # Local development server
    port = int(os.getenv('PORT', '5000'))
    print(f"🚀 Starting local SkillUp server on port {port}...")
    print(f"📡 API Environment: {'LOCAL' if IS_LOCAL else 'PRODUCTION'}")
    app.run(debug=True, host='0.0.0.0', port=port)
