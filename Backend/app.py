import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from .api.routes import api_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register Blueprint
    app.register_blueprint(api_bp)
    
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('PORT', '5000'))
    IS_LOCAL = os.getenv('VERCEL') != '1' and os.getenv('VERCEL_ENV') is None
    
    print(f"🚀 Starting SkillUp server (Layered Architecture) on port {port}...")
    print(f"📡 Environment: {'LOCAL' if IS_LOCAL else 'PRODUCTION'}")
    
    app.run(debug=True, host='0.0.0.0', port=port)
