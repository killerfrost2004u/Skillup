from flask import Flask, jsonify
import pyodbc
import os
from dotenv import load_dotenv
from decimal import Decimal
import datetime

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    """Use the proven working connection"""
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
    """Convert database values to JSON-serializable types"""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime.datetime):
        return value.isoformat()
    elif isinstance(value, datetime.date):
        return value.isoformat()
    else:
        return value


@app.route('/')
def home():
    return jsonify({
        "message": "E-Learning Platform API - Connected Successfully! 🎉",
        "status": "Running",
        "database": "elearning_platform",
        "endpoints": {
            "test_db": "/test-db",
            "users": "/users",
            "courses": "/courses",
            "lessons": "/lessons",
            "enrollments": "/enrollments",
            "payments": "/payments",
            "reviews": "/reviews"
        }
    })


@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Get server and database info
            cursor.execute("SELECT @@SERVERNAME as server, DB_NAME() as db")
            info = cursor.fetchone()

            # Get table counts
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


# API endpoints for all tables
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


def get_table_data(table_name):
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


# Additional useful endpoints
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
    print("📍 Server: localhost\\SQLEXPRESS")
    print("💾 Database: elearning_platform")
    print("🌐 API running on: http://localhost:5000")
    print("\n📚 Available endpoints:")
    print("   GET /              - API information")
    print("   GET /test-db       - Test database connection")
    print("   GET /users         - Get all users")
    print("   GET /courses       - Get all courses")
    print("   GET /lessons       - Get all lessons")
    print("   GET /enrollments   - Get all enrollments")
    print("   GET /payments      - Get all payments")
    print("   GET /reviews       - Get all reviews")
    print("   GET /course/<id>/lessons - Get lessons for a course")
    print("   GET /user/<id>/enrollments - Get user enrollments")

    app.run(debug=True, host='0.0.0.0', port=5000)