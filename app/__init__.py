from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.extensions import db, mail, login_manager
from app.config import Config
from app.models.user import User  # 👈 Add this import
from app.models.topic import Topic,UserTopicProgress
from app.models.test_topic import test_topics
from app.models.test import Test
from app.models.test_question import TestQuestion
from app.models.coding_test import CodingTest
from app.models.coding_question import CodingQuestion   
from app.models.coding_test_topic import coding_test_topics
from app.models.coding_test_question import coding_test_questions
from app.models.coding_test_progress import CodingTestProgress          
from app.models.badge import Badge, UserBadge

from app.models.topic import UserTopicProgress  # 👈 Add this import
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Flask-Login setup
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register Blueprints
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.study import study_bp
    from app.routes.admin_coding import admin_coding_bp
    from app.routes.coding import coding_bp
    from app.routes.admin_coding_test import admin_coding_test_bp   
    from app.routes.coding_test import coding_test_bp
    from app.routes.badge import badge_bp



    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(study_bp)
    app.register_blueprint(admin_coding_bp)
    app.register_blueprint(coding_bp)
    app.register_blueprint(admin_coding_test_bp)
    app.register_blueprint(coding_test_bp)
    app.register_blueprint(badge_bp)




    @app.route("/")
    def home():
        return "<h3>Welcome to DSA Learning Platform 👋</h3><p><a href='/auth/login'>Login</a> | <a href='/auth/signup'>Signup</a></p>"

    return app
