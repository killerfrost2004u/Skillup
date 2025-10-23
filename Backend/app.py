from flask import Flask, jsonify
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)


# Database configuration
def get_db_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')};"
            f"SERVER={os.getenv('DB_SERVER', 'localhost')};"
            f"DATABASE={os.getenv('DB_NAME', 'YourDatabaseName')};"
            f"UID={os.getenv('DB_USER', 'sa')};"
            f"PWD={os.getenv('DB_PASSWORD', '')}"
        )
        return conn
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        return None


# Test route to check database connection
@app.route('/')
def home():
    return jsonify({"message": "Flask SQL Server Backend is running!"})


# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users")
            users = cursor.fetchall()

            # Convert to list of dictionaries
            users_list = []
            for user in users:
                users_list.append({
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'password': user[3],
                    'role': user[4]
                })

            conn.close()
            return jsonify(users_list)
        except pyodbc.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500


# Get all courses
@app.route('/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Courses")
            courses = cursor.fetchall()

            courses_list = []
            for course in courses:
                courses_list.append({
                    'id': course[0],
                    'title': course[1],
                    'description': course[2],
                    'instructor_id': course[3],
                    'price': float(course[4])
                })

            conn.close()
            return jsonify(courses_list)
        except pyodbc.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500


# Get enrollments
@app.route('/enrollments', methods=['GET'])
def get_enrollments():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Enrollments")
            enrollments = cursor.fetchall()

            enrollments_list = []
            for enrollment in enrollments:
                enrollments_list.append({
                    'id': enrollment[0],
                    'user_id': enrollment[1],
                    'course_id': enrollment[2],
                    'date_enrolled': enrollment[3].strftime('%Y-%m-%d')
                })

            conn.close()
            return jsonify(enrollments_list)
        except pyodbc.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500


# Test database connection
@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT @@version")
            version = cursor.fetchone()
            conn.close()
            return jsonify({
                "status": "Database connected successfully",
                "sql_server_version": version[0]
            })
        except pyodbc.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)