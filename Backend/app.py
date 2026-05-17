import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging

from .data.repository import UserRepository, CourseRepository
from .services.auth_service import AuthService
from .services.course_service import CourseService, AIChatService, CompletionLogger, OpenAIStrategy, OllamaStrategy
from .api.routes import api_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 1. Instantiate Repositories (Data Layer)
    from .data.db import db_manager
    user_repo = UserRepository(db_manager)
    course_repo = CourseRepository(db_manager)
    
    # 2. Instantiate Services (Brain Layer) with DI
    auth_service = AuthService(user_repo)
    course_service = CourseService(course_repo)
    
    # Select AI Strategy
    openai_key = os.getenv('OPENAI_API_KEY')
    chat_strategy = OpenAIStrategy(openai_key) if openai_key else OllamaStrategy()
    ai_service = AIChatService(chat_strategy)
    
    # 3. Attach Observers (Behavioral Pattern)
    course_service.add_observer(CompletionLogger())
    
    # 4. Inject Services into Routes (Blueprint context)
    # Since Blueprints are static, we'll attach services to the app object 
    # or use a more advanced DI container. For simplicity, we use app.config 
    # or custom attributes.
    app.auth_service = auth_service
    app.course_service = course_service
    app.ai_service = ai_service
    app.user_repo = user_repo # For profile updates
    
    # Register Blueprint
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('PORT', '5000'))
    IS_LOCAL = os.getenv('VERCEL') != '1' and os.getenv('VERCEL_ENV') is None
    
    print(f"🚀 Starting SkillUp server (Pattern Integrated) on port {port}...")
    print(f"📡 Environment: {'LOCAL' if IS_LOCAL else 'PRODUCTION'}")
    
    app.run(debug=True, host='0.0.0.0', port=port)
