from flask import Flask
from flask_jwt_extended import JWTManager

from backend.config.config import Config
from backend.models import init_db
from backend.helpers.user_helpers import create_default_admin

from backend.routes.auth_routes import auth_bp
from backend.routes.item_routes import item_bp
from backend.routes.claim_routes import claim_bp
from backend.routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt = JWTManager(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(item_bp, url_prefix="/api")
    app.register_blueprint(claim_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Initialize DB
    init_db()
    create_default_admin()

    return app
