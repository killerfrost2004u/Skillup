from flask import Flask, jsonify, request
import pyodbc
import os
from dotenv import load_dotenv
from decimal import Decimal
import datetime
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import json

# Load environment variables (like DB connection details)
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes (allow access from frontend URL)
CORS(app)

# Initialize Flask-Bcrypt for secure passwords
bcrypt = Bcrypt(app)


# --- Database Connection and Utility Functions ---

def get_db_connection():
    """Establishes a connection to the SQL Server database."""
    try:
        conn_str = (
            f"DRIVER={os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')};"
            f"SERVER={os.getenv('DB_SERVER', 'localhost\\SQLEXPRESS')};"
            f"DATABASE={os.getenv('DB_NAME', 'elearning_platform')};"
            f"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        return None


def serialize_value(value):
    """Converts database values (Decimal, datetime) to JSON-serializable types."""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime.datetime):
        return value.isoformat()
    elif isinstance(value, datetime.date):
        return value.isoformat()
    else:
        return value


def get_table_data(table_name):
    """Generic function to fetch all data from a specified table."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        data = []

        for row in cursor.fetchall():
            row_data = {}
            for i, value in enumerate(row):
                row_data[columns[i]] = serialize_value(value)
            data.append(row_data)

        conn.close()
        return jsonify({
            "table": table_name,
            "count": len(data),
            "data": data
        })
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


# --- Authentication Endpoints (Method: POST) ---

@app.route('/register', methods=['POST'])
def register_user():
    """Handles new user registration."""
    try:
        data = request.get_json()
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({"message": "Missing username, email, or password"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = conn.cursor()

            # Check if user already exists (by email)
            cursor.execute("SELECT email FROM Users WHERE email = ?", email)
            if cursor.fetchone():
                conn.close()
                return jsonify({"message": "User with this email already exists"}), 409

            # Hash the password using bcrypt
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the new user into the Users table
            insert_query = """
            INSERT INTO Users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, name, email, hashed_password, 'student')
            conn.commit()
            conn.close()

            return jsonify({
                "message": "Registration successful! Welcome to SkillUp.",
                "user": {"name": name, "email": email}
            }), 201

        except pyodbc.Error as e:
            conn.rollback()
            conn.close()
            print(f"Database registration failed: {e}")
            return jsonify({"error": "Database error during registration. Check server logs."}), 500

    except Exception as e:
        print(f"General error during registration: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500


@app.route('/login', methods=['POST'])
def login_user():
    """Handles user login."""
    try:
        data = request.get_json()
        name = data.get('username')
        password = data.get('password')

        if not all([name, password]):
            return jsonify({"message": "Missing username or password"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = conn.cursor()

            # Retrieve user data by name
            cursor.execute("SELECT user_id, name, email, password, role FROM Users WHERE name = ?", name)
            user_record = cursor.fetchone()
            columns = [column[0] for column in cursor.description]
            conn.close()

            if user_record:
                user = dict(zip(columns, user_record))

                # Verify the hashed password
                if bcrypt.check_password_hash(user['password'], password):
                    return jsonify({
                        "message": "Login successful!",
                        "user_id": user['user_id'],
                        "username": user['name'],
                        "role": user['role']
                    }), 200
                else:
                    return jsonify({"message": "Invalid username or password"}), 401
            else:
                return jsonify({"message": "Invalid username or password"}), 401

        except pyodbc.Error as e:
            print(f"Database login check failed: {e}")
            return jsonify({"error": "Database error during login check."}), 500

    except Exception as e:
        print(f"General error during login: {e}")
        return jsonify({"error": "An unexpected server error occurred."}), 500


# --- General and Existing Endpoints ---

@app.route('/')
def home():
    return jsonify({
        "message": "E-Learning Platform API - Connected Successfully! 🎉",
        "status": "Running",
        "database": "elearning_platform",
        "endpoints": {
            "test_db": "/test-db",
            "register": "/register (POST - Auth)",
            "login": "/login (POST - Auth)",
            "users": "/users",
            "courses": "/courses",
            "lessons": "/lessons",
            "enrollments": "/enrollments",
            "payments": "/payments",
            "reviews": "/reviews",
            "course_lessons": "/course/<id>/lessons",
            "user_enrollments": "/user/<id>/enrollments"
        }
    })

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT @@SERVERNAME as server, DB_NAME() as db")
            info = cursor.fetchone()
            tables = {}
            for table in ['Users', 'Courses', 'Lessons', 'Enrollments', 'Payments', 'Reviews']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    tables[table] = cursor.fetchone()[0]
                except:
                    tables[table] = "Table not found"
            conn.close()
            return jsonify({
                "status": "success",
                "server": info.server,
                "database": info.db,
                "table_counts": tables
            })
        except pyodbc.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/users')
def get_users():
    return get_table_data('Users')

@app.route('/courses')
def get_courses():
    return get_table_data('Courses')

@app.route('/lessons')
def get_lessons():
    return get_table_data('Lessons')

@app.route('/enrollments')
def get_enrollments():
    return get_table_data('Enrollments')

@app.route('/payments')
def get_payments():
    return get_table_data('Payments')

@app.route('/reviews')
def get_reviews():
    return get_table_data('Reviews')


@app.route('/course/<int:course_id>/lessons')
def get_course_lessons(course_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, c.title as course_title 
            FROM Lessons l 
            JOIN Courses c ON l.course_id = c.course_id 
            WHERE l.course_id = ?
            ORDER BY l.position
        """, course_id)

        columns = [column[0] for column in cursor.description]
        lessons = []

        for row in cursor.fetchall():
            lesson_data = {}
            for i, value in enumerate(row):
                lesson_data[columns[i]] = serialize_value(value)
            lessons.append(lesson_data)

        conn.close()
        return jsonify({
            "course_id": course_id,
            "lessons": lessons
        })
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route('/user/<int:user_id>/enrollments')
def get_user_enrollments(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, c.title, c.description, u.name as user_name
            FROM Enrollments e
            JOIN Courses c ON e.course_id = c.course_id
            JOIN Users u ON e.user_id = u.user_id
            WHERE e.user_id = ?
        """, user_id)

        columns = [column[0] for column in cursor.description]
        enrollments = []

        for row in cursor.fetchall():
            enrollment_data = {}
            for i, value in enumerate(row):
                enrollment_data[columns[i]] = serialize_value(value)
            enrollments.append(enrollment_data)

        conn.close()
        return jsonify({
            "user_id": user_id,
            "enrollments": enrollments
        })
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting E-Learning Platform API...")
    print("🌐 API running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
