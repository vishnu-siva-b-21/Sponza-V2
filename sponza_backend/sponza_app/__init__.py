from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sponza_app.config import Config
from flask_caching import Cache 
from sponza_app.worker import celery_init_app

cache = Cache()
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            timezone="Asia/Kolkata",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    mail.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)

    @app.before_request
    def make_session_permanent():
        session.permanent = False

    # Importing all blueprints
    from sponza_app.modules.main import main
    from sponza_app.modules.influencer import influencer
    from sponza_app.modules.sponsor import sponsor
    from sponza_app.modules.admin import admin
    from sponza_app.modules.errors import errors

    # Register all blueprints, setting their URL prefix
    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(influencer, url_prefix="/influencer")
    app.register_blueprint(sponsor, url_prefix="/sponsor")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(errors)


    def add_admin():
        from sponza_app.models import Admin

        existing_user = Admin.query.filter_by(email="admin@gmail.com").first()
        if existing_user is None:
            hashed_password = bcrypt.generate_password_hash("admin").decode("utf-8")
            admin = Admin(
                email="admin@gmail.com",
                password=hashed_password,
            )
            db.session.add(admin)
            db.session.commit()


    # Initialize the application
    with app.app_context():
        db.create_all()
        add_admin()

    return app
