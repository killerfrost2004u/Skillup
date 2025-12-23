from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------------------
# Database Configuration
# -------------------------------
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()  # 'sqlite' or 'sqlserver'

# Global database variables (will be initialized later)
conn = None
cursor = None


def init_sqlite_db():
    """Initialize SQLite database with tables"""
    global conn, cursor

    conn = sqlite3.connect('skill_up.db', check_same_thread=False)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        profile_image TEXT DEFAULT 'user.jpg',
        age INTEGER,
        year TEXT,
        major TEXT,
        college TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Courses (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        description TEXT,
        instructor TEXT,
        category TEXT
    )
    ''')

    # Create StudentLectureProgress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS StudentLectureProgress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        progress_percent INTEGER DEFAULT 0,
        last_accessed TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES Users(user_id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id)
    )
    ''')

    # Insert sample courses if empty
    cursor.execute("SELECT COUNT(*) FROM Courses")
    if cursor.fetchone()[0] == 0:
        sample_courses = [
            ('Python Programming', 'Learn Python from scratch', 'Dr. Smith', 'Programming'),
            ('Web Development', 'Full-stack web development', 'Dr. Johnson', 'Web'),
            ('Data Science', 'Data analysis and visualization', 'Dr. Williams', 'Data'),
            ('Machine Learning', 'AI and ML fundamentals', 'Dr. Brown', 'AI')
        ]
        cursor.executemany("INSERT INTO Courses (course_name, description, instructor, category) VALUES (?, ?, ?, ?)",
                           sample_courses)

        # Add sample progress for demo user
        cursor.execute("INSERT INTO Users (name, email, password) VALUES ('demo', 'demo@example.com', 'demo123')")

        for i in range(1, 5):
            cursor.execute(
                "INSERT INTO StudentLectureProgress (student_id, course_id, progress_percent) VALUES (1, ?, ?)",
                (i, i * 20))

    conn.commit()
    print("✅ SQLite database initialized successfully!")


def create_db_connection():
    """Create database connection based on DB_TYPE"""
    global conn, cursor

    if DB_TYPE == 'sqlserver':
        try:
            import pyodbc
            server = os.getenv('DB_SERVER', 'localhost\\SQLEXPRESS')
            database = os.getenv('DB_NAME', 'skill_up')
            username = os.getenv('DB_USERNAME', '')
            password = os.getenv('DB_PASSWORD', '')
            trusted_connection = os.getenv('DB_TRUSTED_CONNECTION', 'yes')

            if trusted_connection.lower() == 'yes':
                conn_str = (
                    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                    f'SERVER={server};'
                    f'DATABASE={database};'
                    f'Trusted_Connection={trusted_connection};'
                    f'TrustServerCertificate=yes;'
                )
            else:
                conn_str = (
                    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                    f'SERVER={server};'
                    f'DATABASE={database};'
                    f'UID={username};'
                    f'PWD={password};'
                    f'TrustServerCertificate=yes;'
                )

            print(f"🔗 Attempting SQL Server connection: {server}/{database}")
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            print("✅ SQL Server connection successful!")
        except ImportError:
            print("⚠️ pyodbc not installed, falling back to SQLite")
            init_sqlite_db()
        except Exception as e:
            print(f"❌ SQL Server connection failed: {e}")
            print("🔄 Falling back to SQLite...")
            init_sqlite_db()
    else:
        # Default to SQLite
        init_sqlite_db()


# Initialize database
create_db_connection()


# -------------------------------
# Database Helper Functions
# -------------------------------
def execute_query(query, params=()):
    """Execute SQL query (works with both SQLite and SQL Server)"""
    global cursor, conn

    if not cursor:
        print("❌ Database not initialized")
        return False

    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        else:
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Query error: {e}")
        if conn:
            conn.rollback()
        return False


def get_user_by_credentials(username, password):
    """Get user by username and password"""
    result = execute_query(
        "SELECT user_id, name, email, role, profile_image, age, year, major, college, notes FROM Users WHERE name=? AND password=?",
        (username, password)
    )
    return result[0] if result else None


# -------------------------------
# REGISTER
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = "student"
    default_image = "user.jpg"

    if not all([username, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if email exists
    result = execute_query("SELECT * FROM Users WHERE email=?", (email,))
    if result:
        return jsonify({"message": "Email already exists"}), 400

    # Insert new user
    success = execute_query(
        "INSERT INTO Users (name, email, password, role, profile_image) VALUES (?, ?, ?, ?, ?)",
        (username, email, password, role, default_image)
    )

    if success:
        return jsonify({"message": "Registration successful"}), 201
    else:
        return jsonify({"message": "Failed to register user"}), 500


# -------------------------------
# LOGIN
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = get_user_by_credentials(username, password)

    if user:
        return jsonify({
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "profile_image": user[4] or "user.jpg",
            "age": user[5],
            "year": user[6],
            "major": user[7],
            "college": user[8]
        }), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


# -------------------------------
# SAVE PROFILE IMAGE
# -------------------------------
@app.route('/save-profile-image', methods=['POST'])
def save_profile_image():
    data = request.get_json()
    email = data.get('email')
    profile_image = data.get('profile_image')

    if not email or not profile_image:
        return jsonify({"message": "Email or profile_image missing"}), 400

    success = execute_query(
        "UPDATE Users SET profile_image=? WHERE email=?",
        (profile_image, email)
    )

    if success:
        return jsonify({"message": "Profile image updated successfully!"}), 200
    else:
        return jsonify({"message": "Failed to update profile image"}), 500


# -------------------------------
# UPDATE PROFILE
# -------------------------------
@app.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    username = data.get('name')
    email = data.get('email')
    profile_image = data.get('profile_image')
    age = data.get('age')
    year = data.get('year')
    major = data.get('major')
    college = data.get('college')

    # Check if email is used by another user
    result = execute_query("SELECT user_id FROM Users WHERE email=? AND name<>?", (email, username))
    if result:
        return jsonify({"message": "Email already used by another user"}), 400

    success = execute_query("""
        UPDATE Users
        SET profile_image=?, age=?, year=?, major=?, college=?
        WHERE name=? AND email=?
    """, (profile_image, age, year, major, college, username, email))

    if success:
        return jsonify({"message": "Profile updated successfully!"}), 200
    else:
        return jsonify({"message": "Failed to update profile"}), 500


# -------------------------------
# GET PROGRESS
# -------------------------------
@app.route('/get-progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    result = execute_query("""
        SELECT c.course_name, s.progress_percent
        FROM StudentLectureProgress s
        JOIN Courses c ON s.course_id = c.course_id
        WHERE s.student_id = ?
    """, (user_id,))

    if result:
        progress_list = [{"course_name": row[0], "progress": row[1]} for row in result]
        return jsonify(progress_list), 200
    else:
        return jsonify([]), 200


# -------------------------------
# CONTACT
# -------------------------------
@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    # Always log the contact attempt
    print(f"📧 Contact form submission:")
    print(f"   Name: {name}")
    print(f"   Email: {email}")
    print(f"   Message: {message[:50]}...")

    # Try to send email
    try:
        if send_email(name, email, message):
            return jsonify({"message": "Message sent successfully!"}), 200
        else:
            return jsonify({"message": "Message received (email not configured)"}), 200
    except Exception as e:
        print(f"Contact error: {e}")
        return jsonify({"message": "Message logged successfully"}), 200


# -------------------------------
# Email Function (Optional)
# -------------------------------
def send_email(name, email, message):
    """Send email - works without email config"""
    smtp_server = os.getenv('SMTP_SERVER')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    if not all([smtp_server, sender_email, sender_password]):
        print("⚠️ Email not configured - message logged to console only")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = sender_email
        msg["Subject"] = f"New Contact Form Message from {name}"

        body = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, sender_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


# -------------------------------
# ADDITIONAL UTILITY ENDPOINTS
# -------------------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "database": DB_TYPE,
        "database_connected": conn is not None,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/reset-demo', methods=['POST'])
def reset_demo():
    """Reset database to demo state (for testing)"""
    if DB_TYPE == 'sqlite':
        # Close current connection
        if conn:
            conn.close()

        # Delete SQLite file
        if os.path.exists('skill_up.db'):
            os.remove('skill_up.db')

        # Reinitialize database
        create_db_connection()

        return jsonify({"message": "Demo database reset successfully!"}), 200
    else:
        return jsonify({"message": "Reset only available for SQLite demo mode"}), 400


# -------------------------------
# TEST ENDPOINT
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-Learning Platform API</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .card {{ background: #f4f4f4; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .success {{ color: green; font-weight: bold; }}
            .warning {{ color: orange; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 E-Learning Platform API</h1>
            <p><span class="success">Status: Running ✅</span></p>
            <p>Database Type: <strong>{DB_TYPE.upper()}</strong></p>
            <p>Database Connected: <strong>{'Yes ✅' if conn else 'No ❌'}</strong></p>

            <div class="card">
                <h3>📚 Available Endpoints:</h3>
                <ul>
                    <li><strong>POST /register</strong> - Register new user</li>
                    <li><strong>POST /login</strong> - User login</li>
                    <li><strong>POST /contact</strong> - Send contact message</li>
                    <li><strong>POST /save-profile-image</strong> - Update profile image</li>
                    <li><strong>POST /update-profile</strong> - Update profile info</li>
                    <li><strong>GET /get-progress/&lt;user_id&gt;</strong> - Get learning progress</li>
                    <li><strong>GET /api/health</strong> - Health check</li>
                    <li><strong>POST /api/reset-demo</strong> - Reset demo data</li>
                </ul>
            </div>

            <div class="card">
                <h3>⚙️ Configuration:</h3>
                <p>Current database: <code>{DB_TYPE}</code></p>
                <p>To switch to SQL Server, create a <code>.env</code> file with:</p>
                <pre>
DB_TYPE=sqlserver
DB_SERVER=localhost\\SQLEXPRESS
DB_NAME=skill_up
                </pre>
            </div>

            <div class="card">
                <h3>🚀 Quick Start:</h3>
                <p>1. Install dependencies: <code>pip install Flask Flask-CORS python-dotenv</code></p>
                <p>2. Run the server: <code>python app.py</code></p>
                <p>3. Test with Postman or your frontend</p>
                <p><strong>Demo credentials:</strong> username: <code>demo</code>, password: <code>demo123</code></p>
            </div>
        </div>
    </body>
    </html>
    """


# -------------------------------
if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    host = os.getenv('HOST', '0.0.0.0')

    print("\n" + "=" * 50)
    print("🚀 E-Learning Platform API")
    print("=" * 50)
    print(f"📊 Database: {DB_TYPE.upper()}")
    print(f"🌐 Server: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"📁 SQLite file: {'skill_up.db' if DB_TYPE == 'sqlite' else 'N/A'}")
    print(f"🔌 Database connected: {'Yes ✅' if conn else 'No ❌'}")
    print("\n📋 Sample credentials for testing:")
    print("   Username: demo")
    print("   Password: demo123")
    print("=" * 50 + "\n")

    app.run(debug=True, host=host, port=port)