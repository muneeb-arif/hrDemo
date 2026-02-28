import os
from dotenv import load_dotenv

load_dotenv()


def _load_secrets_toml():
    """Load secrets from secrets.toml file if it exists"""
    secrets = {}
    secrets_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets.toml')
    
    if os.path.exists(secrets_file):
        try:
            import toml
            with open(secrets_file, 'r') as f:
                secrets = toml.load(f)
        except ImportError:
            # Fallback: simple parsing if toml library not available
            with open(secrets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        secrets[key] = value
        except Exception as e:
            print(f"Warning: Could not load secrets.toml: {e}")
    
    return secrets


# Load secrets from secrets.toml
_secrets = _load_secrets_toml()


def _get_config_value(key: str, default=None):
    """Get config value from secrets.toml, then environment variable, then default"""
    # First try secrets.toml
    if key in _secrets:
        return _secrets[key]
    # Then try environment variable
    value = os.getenv(key)
    if value:
        return value
    # Finally return default
    return default


class Config:
    """Application configuration"""
    # Database
    SQLALCHEMY_DATABASE_URI = _get_config_value('DATABASE_URL', 'sqlite:///hr_demo.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = _get_config_value('JWT_SECRET_KEY', os.urandom(32).hex())
    JWT_ALGORITHM = _get_config_value('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(_get_config_value('JWT_EXPIRATION_HOURS', '24'))
    
    # OpenAI - reads from secrets.toml first, then environment variable
    OPENAI_API_KEY = _get_config_value('OPENAI_API_KEY')
    
    # Flask
    SECRET_KEY = _get_config_value('SECRET_KEY', os.urandom(32).hex())
    DEBUG = _get_config_value('FLASK_ENV', 'development') == 'development'
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_uploads')
