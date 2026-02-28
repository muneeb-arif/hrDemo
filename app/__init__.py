from flask import Flask, request, Response
from flask_cors import CORS
from flasgger import Swagger
from app.config import Config
from app.database import db, init_db


def create_app(config_class=Config):
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for React frontend
    
    # Register blueprints first (needed for Swagger to discover routes)
    from app.api import auth as auth_bp, hr as hr_bp, autosphere as autosphere_bp
    app.register_blueprint(auth_bp.bp, url_prefix='/api/auth')
    app.register_blueprint(hr_bp.bp, url_prefix='/api/hr')
    app.register_blueprint(autosphere_bp.bp, url_prefix='/api/autosphere')
    
    # Initialize Swagger after blueprints are registered
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/swagger"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Enterprise AI Dashboard API",
            "description": "Flask REST API for HR AI Platform and AutoSphere Motors AI Assistant",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme"
            }
        },
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication endpoints"
            },
            {
                "name": "HR AI Platform",
                "description": "HR AI Platform endpoints"
            },
            {
                "name": "AutoSphere Motors",
                "description": "AutoSphere Motors AI Assistant endpoints"
            }
        ]
    }
    
    try:
        swagger = Swagger(app, config=swagger_config, template=swagger_template)
    except Exception as e:
        print(f"Warning: Swagger initialization error: {e}")
        # Continue without Swagger if there's an error
    
    # Protect Swagger UI with basic auth (but allow /apispec.json to be accessed by Swagger UI)
    @app.before_request
    def protect_swagger():
        # Protect the Swagger UI page itself
        if request.path == '/swagger' or (request.path.startswith('/swagger/') and not request.path.startswith('/swagger/static')):
            auth = request.authorization
            if not auth or auth.username != 'swagger' or auth.password != '!!swagger!!':
                return Response(
                    'Swagger UI requires authentication.\n'
                    'Username: swagger\n'
                    'Password: !!swagger!!', 401,
                    {'WWW-Authenticate': 'Basic realm="Swagger UI Login Required"'})
        # Protect static files
        elif request.path.startswith('/flasgger_static'):
            auth = request.authorization
            if not auth or auth.username != 'swagger' or auth.password != '!!swagger!!':
                return Response(
                    'Swagger UI requires authentication.\n'
                    'Username: swagger\n'
                    'Password: !!swagger!!', 401,
                    {'WWW-Authenticate': 'Basic realm="Swagger UI Login Required"'})
        # Allow /apispec.json to be accessed (Swagger UI needs it to load the spec)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    return app
