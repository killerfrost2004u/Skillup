from flask import Blueprint, request, jsonify
from functools import wraps
from ..services.auth_service import AuthService
from ..services.course_service import CourseService, AIChatService
from ..data.repository import UserRepository
import os

api_bp = Blueprint('api', __name__)

IS_LOCAL = os.getenv('VERCEL') != '1' and os.getenv('VERCEL_ENV') is None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        user = AuthService.validate_token(token)
        if not user:
            return jsonify({'message': 'Invalid or expired token!'}), 401
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result = AuthService.register_user(
        data.get("username"), 
        data.get("email"), 
        data.get("password"),
        data.get("role", "student")
    )
    if "error" in result:
        return jsonify({"message": result["error"]}), result["status"]
    return jsonify({"message": result["message"]}), result["status"]

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result = AuthService.login_user(data.get("username"), data.get("password"))
    if "error" in result:
        return jsonify({"message": result["error"]}), result["status"]
    return jsonify(result["data"]), result["status"]

@api_bp.route('/api/check-auth', methods=['GET'])
def check_auth():
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
    
    if not token:
        return jsonify({'authenticated': False}), 200
    
    user = AuthService.validate_token(token)
    if user:
        return jsonify({'authenticated': True, 'user': user}), 200
    return jsonify({'authenticated': False}), 200

@api_bp.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    # Using email as unique identifier for updates as per current frontend
    success = UserRepository.update_profile_by_email(
        data.get('email'),
        data.get('name'),
        data.get('profile_image'),
        data.get('age'),
        data.get('year'),
        data.get('major'),
        data.get('college')
    )
    if success:
        return jsonify({"message": "Profile updated successfully"}), 200
    return jsonify({"message": "Failed to update profile"}), 500

@api_bp.route('/chat', methods=['POST'])
def chat():
    if not IS_LOCAL:
        return jsonify({'reply': 'Chat available in local environment only.', 'error': 'Restricted'}), 403
    
    data = request.get_json()
    reply = AIChatService.get_reply(data.get('message', ''))
    return jsonify({'reply': reply})

@api_bp.route('/courses', methods=['GET'])
def get_courses():
    return jsonify(CourseService.get_all_courses()), 200

@api_bp.route('/get-progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    return jsonify(CourseService.get_user_progress(user_id)), 200

@api_bp.route('/api/progress/save', methods=['POST'])
def save_progress():
    data = request.get_json()
    result = CourseService.save_progress(data.get('user_id'), data)
    return jsonify(result), 200

@api_bp.route('/api/progress/<int:user_id>/<string:playlist_id>', methods=['GET'])
def get_playlist_progress(user_id, playlist_id):
    return jsonify(CourseService.get_playlist_progress(user_id, playlist_id)), 200

@api_bp.route('/api/check-video-access/<string:playlist_id>', methods=['GET'])
@token_required
def check_video_access(playlist_id):
    return jsonify({"has_access": True, "user_id": request.current_user['user_id']}), 200
