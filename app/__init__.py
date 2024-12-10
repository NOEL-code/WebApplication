from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.profiles import bp as profiles_bp
    from app.routes.proposals import bp as proposals_bp
    from app.routes.likes import bp as likes_bp
    from app.routes.block import blocks_bp  # blocks 블루프린트 추가
    from app.routes.preferences import bp as preferences_bp  # blocks 블루프린트 추가

    app.register_blueprint(preferences_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(proposals_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(blocks_bp)  # blocks 블루프린트 등록

    # Create tables if not exist
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

    return app