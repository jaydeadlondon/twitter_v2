from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://twitter_user:twitter_password@localhost:5432/twitter_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Swagger configuration
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
        "specs_route": "/api/docs"
    }
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Twitter Clone API",
            "description": "Corporate microblogging service API",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "api-key"
            }
        },
        "security": [
            {
                "ApiKeyAuth": []
            }
        ]
    }
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Serve static files
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    # Login endpoint for frontend compatibility
    @app.route('/login')
    def login_page():
        """Simple login page with API keys"""
        try:
            from app.models import User
            users = User.query.all()
            api_keys_html = '<br>'.join([
                f'<strong>{user.username}:</strong> <code>{user.api_key}</code>'
                for user in users
            ])
            
            return f'''
            <html>
            <head>
                <title>Twitter Clone - API Keys</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background: #f0f2f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .key {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #1da1f2; }}
                    .btn {{ display: inline-block; padding: 10px 20px; background: #1da1f2; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
                    .btn:hover {{ background: #0d8bd9; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🐦 Twitter Clone</h1>
                    <h2>API Authentication</h2>
                    <p>Данное приложение использует API ключи для аутентификации.</p>
                    <p><strong>Доступные API ключи:</strong></p>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                        {api_keys_html}
                    </div>
                    <br>
                    <p><strong>Инструкция:</strong></p>
                    <ol>
                        <li>Скопируйте один из API ключей выше</li>
                        <li>Найдите поле для ввода API ключа на главной странице</li>
                        <li>Вставьте ключ и нажмите "Войти" или "Login"</li>
                    </ol>
                    <br>
                    <a href="/" class="btn">🏠 Главная страница</a>
                    <a href="/api/docs" class="btn">📖 API документация</a>
                </div>
            </body>
            </html>
            '''
        except Exception as e:
            return f'<h1>Ошибка: {str(e)}</h1><p><a href="/">Назад</a></p>'
    
    return app