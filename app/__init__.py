from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import db, init_db


def create_app(config_class=Config):
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for React frontend
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register blueprints
    from app.api import auth as auth_bp, hr as hr_bp, autosphere as autosphere_bp
    app.register_blueprint(auth_bp.bp, url_prefix='/api/auth')
    app.register_blueprint(hr_bp.bp, url_prefix='/api/hr')
    app.register_blueprint(autosphere_bp.bp, url_prefix='/api/autosphere')
    
    return app
