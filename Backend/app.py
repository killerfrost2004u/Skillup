from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# -------------------------------
#  Connect to SQL Server
# -------------------------------
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 18 for SQL Server};'
    r'SERVER=ENG_AYA\SQLEXPRESS01;'
    r'DATABASE=skill_up;'
    r'Trusted_Connection=yes;'
    r'TrustServerCertificate=yes;'
    r'Encrypt=no;'
)
cursor = conn.cursor()


# -------------------------------
#  REGISTER
# -------------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = "student"
    default_image = "user.jpg"

    # Check if email already exists
    cursor.execute("SELECT * FROM Users WHERE email=?", (email,))
    if cursor.fetchone():
        return jsonify({"message": "Email already exists"}), 400

    try:
        cursor.execute(
            "INSERT INTO Users (name, email, password, role, profile_image) VALUES (?, ?, ?, ?, ?)",
            (username, email, password, role, default_image)
        )
        conn.commit()

        return jsonify({"message": "Registration successful"}), 201

    except Exception as e:
        return jsonify({"message": "Failed to register user"}), 500


# -------------------------------
#  LOGIN
# -------------------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # جلب بيانات المستخدم بما فيها النوت
    cursor.execute("""
        SELECT user_id,name, email, role, profile_image, age, year, major, college, notes
        FROM Users
        WHERE name=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

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
    profile_image = data.get('profile_image')  # Base64 image string

    if not email or not profile_image:
        return jsonify({"message": "Email or profile_image missing"}), 400

    try:
        cursor.execute(
            "UPDATE Users SET profile_image=? WHERE email=?",
            (profile_image, email)
        )
        conn.commit()
        return jsonify({"message": "Profile image updated successfully!"}), 200
    except Exception as e:
        print("Update failed:", e)
        return jsonify({"message": "Failed to update profile image"}), 500


# -------------------------------
#  TEST
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return "SQL Server Backend Running Successfully!"


# -----------------------------------

# -----------------------------------
# SEND EMAIL FUNCTION
# -----------------------------------
def send_email(name, email, message):
    WEBSITE_EMAIL = "skillup843@gmail.com"
    APP_PASSWORD = "qaat fmoc ylhv skgy"
    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = WEBSITE_EMAIL
    msg["Subject"] = f"New Contact Form Message from {name}"

    body = f"""
    You received a new message from the website contact form:

    Name: {name}
    Email: {email}
    Message:
    {message}
    """

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(WEBSITE_EMAIL, APP_PASSWORD)
    server.sendmail(email, WEBSITE_EMAIL, msg.as_string())
    server.quit()


# -----------------------------------
# CONTACT ROUTE
# -----------------------------------
@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    try:
        send_email(name, email, message)
        return jsonify({"message": "Message sent successfully!"}), 200

    except Exception as e:
        print("Email error:", e)
        return jsonify({"message": "Failed to send message"}), 500


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

    try:
        cursor.execute("SELECT user_id FROM Users WHERE email=? AND name<>?", (email, username))
        if cursor.fetchone():
            return jsonify({"message": "Email already used by another user"}), 400

        cursor.execute("""
            UPDATE Users
            SET profile_image=?, age=?, year=?, major=?, college=?
            WHERE name=? AND email=?
        """, (profile_image, age, year, major, college, username, email))
        conn.commit()
        return jsonify({"message": "Profile updated successfully!"}), 200
    except Exception as e:
        print("Update failed:", e)
        return jsonify({"message": "Failed to update profile"}), 500


@app.route('/get-progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    cursor.execute("""
        SELECT c.course_name, s.progress_percent
        FROM StudentLectureProgress s
        JOIN Courses c ON s.course_id = c.course_id
        WHERE s.student_id = ?
    """, (user_id,))
    data = cursor.fetchall()

    progress_list = [{"course_name": row[0], "progress": row[1]} for row in data]
    return jsonify(progress_list), 200


# -------------------------------
if __name__ == '__main__':
    print("🚀 Starting E-Learning Platform API...")
    print("🌐 API running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
