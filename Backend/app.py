from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import pyodbc
import os
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import google.genai as genai  # Updated import
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
DB_CONFIG = {
    'server': os.getenv('DB_SERVER', 'localhost\\SQLEXPRESS'),
    'database': os.getenv('DB_NAME', 'elearning_platform'),
    'username': os.getenv('DB_USERNAME', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'trusted_connection': os.getenv('DB_TRUSTED_CONNECTION', 'yes').lower() == 'yes'
}


# ============================================
# JWT CONFIGURATION - ADD THIS SECTION
# ============================================
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24


def get_db_connection():
    """Get SQL Server database connection"""
    try:
        if DB_CONFIG['trusted_connection']:
            conn_str = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={DB_CONFIG["server"]};'
                f'DATABASE={DB_CONFIG["database"]};'
                f'Trusted_Connection=yes;'
                f'TrustServerCertificate=yes;'
            )
        else:
            conn_str = (
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={DB_CONFIG["server"]};'
                f'DATABASE={DB_CONFIG["database"]};'
                f'UID={DB_CONFIG["username"]};'
                f'PWD={DB_CONFIG["password"]};'
                f'TrustServerCertificate=yes;'
            )

        conn = pyodbc.connect(conn_str)
        logger.info(f"✅ Connected to SQL Server: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None


# ============================================
# 2. GOOGLE GEMINI CONFIGURATION (UPDATED)
# ============================================
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.warning("⚠️ GOOGLE_API_KEY not found in environment variables")
    gemini_client = None
else:
    try:
        # Configure Google Gemini with the new API
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
        logger.info(f"✅ Google Gemini client initialized (using google.genai)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Google Gemini: {e}")
        gemini_client = None


# ============================================
# 3. DATABASE HELPER FUNCTIONS
# ============================================
def execute_query(query, params=()):
    """Execute SQL query and return results"""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith('SELECT'):
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            return result
        else:
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"❌ Query error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_user_by_credentials(username, password):
    """Get user by username and password"""
    result = execute_query(
        "SELECT user_id, name, email, role FROM Users WHERE name=? AND password=?",
        (username, password)
    )
    return result[0] if result else None


# ============================================
# PROGRESS STORAGE HELPERS (File-based) - ADD THIS AFTER get_user_by_credentials
# ============================================
PROGRESS_FILE = "user_progress.json"

def load_progress_data():
    """Load progress data from JSON file"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading progress data: {e}")
        return {}

def save_progress_data(data):
    """Save progress data to JSON file"""
    try:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving progress data: {e}")
        return False

def get_user_progress_key(user_id, playlist_id):
    """Generate a unique key for user progress"""
    return f"user_{user_id}_playlist_{playlist_id}"


# ============================================
# AUTHENTICATION MIDDLEWARE - ADD THIS
# ============================================
def token_required(f):
    """Decorator to require valid JWT token"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user = execute_query(
                "SELECT user_id, name, email, role FROM Users WHERE user_id=?",
                (data['user_id'],)
            )
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401

            request.current_user = current_user[0]

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated


# ============================================
# 4. ROUTES
# ============================================

# -------------------------------
# HOME
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "E-Learning Platform API",
        "database": DB_CONFIG["database"],
        "gemini_configured": gemini_client is not None,
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "chat": "POST /chat",
            "courses": "GET /courses",
            "progress": "GET /progress/<user_id>"
        }
    })


# -------------------------------
# REGISTER
# -------------------------------
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

        existing = execute_query("SELECT * FROM Users WHERE email=?", (email,))
        if existing:
            return jsonify({"message": "Email already exists"}), 400

        success = execute_query(
            "INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, password, role)
        )

        if success:
            return jsonify({"message": "Registration successful"}), 201
        else:
            return jsonify({"message": "Failed to register user"}), 500
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({"message": "Internal server error"}), 500


# -------------------------------
# LOGIN
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = get_user_by_credentials(username, password)

        if user:
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
    """Check if user is authenticated"""
    try:
        token = None

        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'authenticated': False}), 200

        # Verify token
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Check if user exists
        user = execute_query(
            "SELECT user_id, name, email, role FROM Users WHERE user_id=?",
            (data['user_id'],)
        )

        if user:
            return jsonify({
                'authenticated': True,
                'user': user[0]
            }), 200
        else:
            return jsonify({'authenticated': False}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'authenticated': False}), 200
    except jwt.InvalidTokenError:
        return jsonify({'authenticated': False}), 200
    except Exception as e:
        logger.error(f"Check auth error: {e}")
        return jsonify({'authenticated': False}), 200


# -------------------------------
# CHAT WITH GOOGLE GEMINI (UPDATED)
# -------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot messages using Google Gemini API"""
    try:
        if not gemini_client:
            return jsonify({
                'reply': 'AI service is currently unavailable. Please check the API configuration.',
                'error': 'Gemini client not initialized'
            }), 503

        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'reply': 'Please send a message.'}), 400

        # Generate response using Google Gemini (new API)
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",  # You can use gemini-1.5-flash or gemini-1.5-pro
            contents=user_message,
            config={
                "temperature": 0.7,
                "max_output_tokens": 500,
                "system_instruction": "You are a helpful e-learning assistant for an Arabic educational platform. Help students with programming courses like Python, Web Development, and other technical subjects. Respond in the same language as the user's question."
            }
        )

        # Extract the response text
        bot_reply = response.text

        return jsonify({
            'reply': bot_reply,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            'reply': 'عذراً، حدث خطأ في معالجة طلبك. الرجاء المحاولة مرة أخرى.',
            'error': str(e)
        }), 500


# -------------------------------
# GET COURSES
# -------------------------------
@app.route('/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        courses = execute_query("SELECT * FROM Courses")
        if courses is not None:
            return jsonify(courses), 200
        else:
            return jsonify({"message": "Failed to fetch courses"}), 500
    except Exception as e:
        logger.error(f"Get courses error: {e}")
        return jsonify({"message": "Internal server error"}), 500


# -------------------------------
# GET USER PROGRESS
# -------------------------------
@app.route('/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    """Get user's course progress"""
    try:
        return jsonify({
            "user_id": user_id,
            "progress": [
                {"course": "Python Basics", "progress": 65},
                {"course": "Web Development", "progress": 30}
            ]
        }), 200
    except Exception as e:
        logger.error(f"Progress error: {e}")
        return jsonify({"message": "Internal server error"}), 500


# ============================================
# PROGRESS ENDPOINTS (No SQL) - ADD AFTER THE EXISTING /progress/<int:user_id> ENDPOINT
# ============================================

# -------------------------------
# SAVE VIDEO PROGRESS (File-based)
# -------------------------------
@app.route('/api/progress/save', methods=['POST'])
def save_video_progress():
    """Save video progress without SQL"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        playlist_id = data.get('playlist_id')
        video_id = data.get('video_id')
        completed = data.get('completed', False)

        if not all([user_id, playlist_id, video_id]):
            return jsonify({"message": "Missing required fields"}), 400

        # Load existing progress
        progress_data = load_progress_data()

        # Create user key
        user_key = get_user_progress_key(user_id, playlist_id)

        # Initialize if not exists
        if user_key not in progress_data:
            progress_data[user_key] = {
                "user_id": user_id,
                "playlist_id": playlist_id,
                "videos": {},
                "last_updated": datetime.now().isoformat()
            }

        # Update video progress
        progress_data[user_key]["videos"][video_id] = {
            "completed": completed,
            "timestamp": datetime.now().isoformat()
        }
        progress_data[user_key]["last_updated"] = datetime.now().isoformat()

        # Save back to file
        if save_progress_data(progress_data):
            return jsonify({
                "success": True,
                "message": "Progress saved",
                "user_id": user_id,
                "video_id": video_id,
                "completed": completed
            }), 200
        else:
            return jsonify({"success": False, "message": "Failed to save progress"}), 500

    except Exception as e:
        logger.error(f"Save progress error: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


# -------------------------------
# GET USER'S PLAYLIST PROGRESS
# -------------------------------
@app.route('/api/progress/<int:user_id>/<string:playlist_id>', methods=['GET'])
def get_user_playlist_progress(user_id, playlist_id):
    """Get user's progress for a playlist"""
    try:
        progress_data = load_progress_data()
        user_key = get_user_progress_key(user_id, playlist_id)

        if user_key in progress_data:
            user_progress = progress_data[user_key]
            videos = user_progress.get("videos", {})

            # Calculate completion percentage
            completed_videos = [v for v in videos.values() if v.get("completed")]
            total_videos = len(videos)
            progress_percentage = 0

            if total_videos > 0:
                progress_percentage = int((len(completed_videos) / total_videos) * 100)

            return jsonify({
                "success": True,
                "user_id": user_id,
                "playlist_id": playlist_id,
                "completed_videos": len(completed_videos),
                "total_videos": total_videos,
                "progress_percentage": progress_percentage,
                "videos": videos,
                "last_updated": user_progress.get("last_updated")
            }), 200
        else:
            # Return empty progress if not found
            return jsonify({
                "success": True,
                "user_id": user_id,
                "playlist_id": playlist_id,
                "completed_videos": 0,
                "total_videos": 0,
                "progress_percentage": 0,
                "videos": {},
                "last_updated": None
            }), 200

    except Exception as e:
        logger.error(f"Get progress error: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


# -------------------------------
# MARK VIDEO AS COMPLETED
# -------------------------------
@app.route('/api/progress/mark-completed', methods=['POST'])
def mark_video_completed():
    """Mark a video as completed for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        playlist_id = data.get('playlist_id')
        video_id = data.get('video_id')

        # Call the save function with completed=true
        return save_video_progress()

    except Exception as e:
        logger.error(f"Mark completed error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# -------------------------------
# CHECK VIDEO ACCESS (PROTECTED)
# -------------------------------
@app.route('/api/check-video-access/<string:playlist_id>', methods=['GET'])
@token_required  # <-- This protects the endpoint
def check_video_access(playlist_id):
    """Check if user has access to playlist videos"""
    try:
        user_id = request.current_user['user_id']

        # Here you can add additional checks:
        # - If user purchased this course
        # - If user is subscribed
        # - Any other business logic

        return jsonify({
            "has_access": True,
            "user_id": user_id,
            "playlist_id": playlist_id,
            "message": "Access granted"
        }), 200

    except Exception as e:
        logger.error(f"Check access error: {e}")
        return jsonify({"message": "Internal server error"}), 500


# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "database": DB_CONFIG["database"],
        "database_connected": get_db_connection() is not None,
        "gemini_configured": gemini_client is not None,
        "timestamp": datetime.now().isoformat()
    }), 200


# -------------------------------
# TEST GEMINI (UPDATED)
# -------------------------------
@app.route('/test-gemini', methods=['GET'])
def test_gemini():
    """Test Google Gemini API connection"""
    if not gemini_client:
        return jsonify({
            "status": "error",
            "message": "Gemini client not initialized. Check GOOGLE_API_KEY in .env file."
        }), 400

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Say 'Hello World' in Arabic"
        )

        return jsonify({
            "status": "success",
            "message": "Google Gemini API is working!",
            "response": response.text
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================
# 5. MAIN ENTRY POINT
# ============================================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 E-Learning Platform API")
    print("=" * 50)
    print(f"📊 Database: {DB_CONFIG['database']}")
    print(f"🔌 Database Server: {DB_CONFIG['server']}")
    print(f"🤖 Google Gemini Configured: {'Yes ✅' if gemini_client else 'No ❌'}")
    print(f"📚 Using google.genai package (new API)")

    if not gemini_client and GOOGLE_API_KEY:
        print(f"⚠️  GOOGLE_API_KEY found but client failed to initialize")
    elif not GOOGLE_API_KEY:
        print(f"⚠️  GOOGLE_API_KEY not found in environment")

    print(f"🌐 Server will run on: http://localhost:5000")
    print("=" * 50 + "\n")

    port = int(os.getenv('PORT', '5000'))
    host = os.getenv('HOST', '0.0.0.0')

    app.run(debug=True, host=host, port=port)