import os
from flask import Flask, session
from models import db, User, News, Test, Question, University, CareerDirection, Vacancy, DailyFact, Achievement
from config import Config
from routes import register_blueprints
from utils.achievements import AchievementManager
from flask_wtf.csrf import CSRFProtect
from datetime import date, timedelta
import json

def create_app(config_class=Config):
    """Фабрика создания приложения"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # CSRF защита
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Инициализация базы данных
    db.init_app(app)
    
    # Добавляем функцию для получения пользователя в шаблоны
    @app.context_processor
    def utility_processor():
        from models import User
        
        def get_user_by_id(user_id):
            return User.query.get(user_id)
        
        def current_user():
            if 'user_id' in session:
                return User.query.get(session['user_id'])
            return None
        
        return dict(get_user_by_id=get_user_by_id, current_user=current_user)
    
    # Регистрация Blueprint'ов
    register_blueprints(app)
    
    # Создание таблиц и начальных данных
    with app.app_context():
        db.create_all()
        AchievementManager.init_achievements()

    return app
