import os
from typing import Type


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://twitter_user:twitter_password@localhost:5432/twitter_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    SWAGGER = {
        'title': 'Twitter Clone API',
        'uiversion': 3,
        'specs_route': '/api/docs/',
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'description': 'Corporate microblogging service API',
        'version': '1.0.0',
        'termsOfService': '',
        'contact': {
            'name': 'API Support',
            'url': 'http://localhost:5000',
            'email': 'support@example.com'
        },
        'license': {
            'name': 'MIT',
            'url': 'https://opensource.org/licenses/MIT'
        }
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production!")
    
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No DATABASE_URL set for production!")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config() -> Type[Config]:
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
