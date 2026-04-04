import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Основная конфигурация приложения"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cosmos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # GigaChat - важно! Берем из переменных окружения
    GIGACHAT_API_KEY = os.environ.get('GIGACHAT_API_KEY', '')
    GIGACHAT_TIMEOUT = 30
    
    # Администратор
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@cosmos.ru')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Сессия
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Пагинация
    NEWS_PER_PAGE = 10
    USERS_PER_PAGE = 20
    
    # Достижения
    LEVELS = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 1000
    }
    
    # Цвета для ачивок
    ACHIEVEMENT_COLORS = {
        'bronze': '#cd7f32',
        'silver': '#c0c0c0',
        'gold': '#ffd700',
        'platinum': '#e5e4e2'
    }