from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import google.genai as genai  # Updated import
import logging

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


def get_db_connection():
    """Get SQL Server database connection"""
    try:
        if DB_CONFIG['trusted_connection']:
            conn_str = (
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
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
            return jsonify({
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"message": "Internal server error"}), 500


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