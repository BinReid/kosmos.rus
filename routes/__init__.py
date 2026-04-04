from flask import Blueprint
from routes.main import main_bp
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.tests import tests_bp
from routes.admin import admin_bp
from routes.career import career_bp

def register_blueprints(app):
    """Регистрация всех Blueprint'ов"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(career_bp)