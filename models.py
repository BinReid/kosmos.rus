from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    avatar_data = db.Column(db.Text, nullable=True)  
    avatar_mime = db.Column(db.String(50), nullable=True)
    level = db.Column(db.Integer, default=1)
    points = db.Column(db.Integer, default=0)
    streak_days = db.Column(db.Integer, default=0)
    last_visit = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    elevator_achievements = db.Column(db.Text, default='[]')

    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    test_results = db.relationship('TestResult', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    read_news = db.relationship('UserReadNews', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_elevator_achievements(self):
        """Получить список достижений космического лифта"""
        import json
        if self.elevator_achievements:
            return json.loads(self.elevator_achievements)
        return []
    
    def add_elevator_achievement(self, event_id):
        """Добавить достижение космического лифта"""
        import json
        achievements = self.get_elevator_achievements()
        if event_id not in achievements:
            achievements.append(event_id)
            self.elevator_achievements = json.dumps(achievements)
            return True
        return False
    
    def has_elevator_achievement(self, event_id):
        """Проверить, есть ли достижение"""
        return event_id in self.get_elevator_achievements()
    
    def get_elevator_progress(self):
        """Получить прогресс (количество полученных достижений)"""
        return len(self.get_elevator_achievements())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_avatar(self):
        if self.avatar_data:
            return f"data:{self.avatar_mime};base64,{self.avatar_data}"
        return None
    
    def is_adult(self):
        """Проверка на совершеннолетие (18+)"""
        return self.age and self.age >= 18
    
    def is_teenager(self):
        """Проверка на возраст от 16 до 17 лет"""
        return self.age and 16 <= self.age <= 17
    
    def has_career_access(self):
        """Доступ к разделу Карьера (16+)"""
        return self.age and self.age >= 16
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'level': self.level,
            'points': self.points,
            'streak_days': self.streak_days,
            'is_admin': self.is_admin
        }


class Achievement(db.Model):
    """Модель достижений"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50), default='🏆')
    color = db.Column(db.String(20), default='gold')
    condition_type = db.Column(db.String(50))  
    condition_value = db.Column(db.Integer, default=1)
    points_reward = db.Column(db.Integer, default=10)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color
        }


class UserAchievement(db.Model):
    """Связь пользователя с достижениями"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    achievement = db.relationship('Achievement', backref='users')


class News(db.Model):
    """Модель новостей"""
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_data = db.Column(db.Text, nullable=True)  
    image_mime = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
    def get_image(self):
        if self.image_data:
            return f"data:{self.image_mime};base64,{self.image_data}"
        return None


class UserReadNews(db.Model):
    """Отметки о прочтении новостей"""
    __tablename__ = 'user_read_news'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    read_at = db.Column(db.DateTime, default=datetime.utcnow)


class Test(db.Model):
    """Модель тестов"""
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='test', lazy='dynamic', cascade='all, delete-orphan')


class Question(db.Model):
    """Модель вопросов"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    options = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Integer, nullable=False)
    
    def get_options(self):
        """Получить варианты ответов в виде списка"""
        try:
            return json.loads(self.options)
        except:
            return ['', '', '', '']
    
    @property
    def option1(self):
        return self.get_options()[0] if len(self.get_options()) > 0 else ''
    
    @property
    def option2(self):
        return self.get_options()[1] if len(self.get_options()) > 1 else ''
    
    @property
    def option3(self):
        return self.get_options()[2] if len(self.get_options()) > 2 else ''
    
    @property
    def option4(self):
        return self.get_options()[3] if len(self.get_options()) > 3 else ''


class TestResult(db.Model):
    """Результаты тестов"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    passed_at = db.Column(db.DateTime, default=datetime.utcnow)


class DailyFact(db.Model):
    """Факт дня"""
    __tablename__ = 'daily_facts'
    
    id = db.Column(db.Integer, primary_key=True)
    fact = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, default=date.today)
    image_data = db.Column(db.Text, nullable=True)
    image_mime = db.Column(db.String(50), nullable=True)
    
    def get_image(self):
        if self.image_data:
            return f"data:{self.image_mime};base64,{self.image_data}"
        return None


class University(db.Model):
    """Модель ВУЗа для подготовки космонавтов"""
    __tablename__ = 'universities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    specialties = db.Column(db.Text, nullable=False) 
    image_data = db.Column(db.Text, nullable=True)
    image_mime = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_image(self):
        if self.image_data:
            return f"data:{self.image_mime};base64,{self.image_data}"
        return None
    
    def get_specialties_list(self):
        try:
            return json.loads(self.specialties)
        except:
            return []
    
    def set_specialties_list(self, specialties):
        self.specialties = json.dumps(specialties, ensure_ascii=False)


class CareerDirection(db.Model):
    """Модель направления в карьере космонавта"""
    __tablename__ = 'career_directions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='🚀')
    content = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Vacancy(db.Model):
    """Модель вакансии (доступно с 18 лет)"""
    __tablename__ = 'vacancies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    location = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.Date, nullable=True)

class Project(db.Model):
    """Модель космических проектов"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.String(300), nullable=False)
    description_full = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='planned') 
    status_name = db.Column(db.String(100), default='В плане')
    mission_type = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    image_data = db.Column(db.Text, nullable=True)
    image_mime = db.Column(db.String(50), nullable=True)
    goals = db.Column(db.Text, nullable=True)  
    partners = db.Column(db.Text, nullable=True)  
    updates = db.Column(db.Text, nullable=True) 
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def get_image(self):
        if self.image_data:
            return f"data:{self.image_mime};base64,{self.image_data}"
        return None
    
    def get_goals_list(self):
        try:
            return json.loads(self.goals) if self.goals else []
        except:
            return []
    
    def set_goals_list(self, goals):
        self.goals = json.dumps(goals, ensure_ascii=False)
    
    def get_partners_list(self):
        try:
            return json.loads(self.partners) if self.partners else []
        except:
            return []
    
    def set_partners_list(self, partners):
        self.partners = json.dumps(partners, ensure_ascii=False)
    
    def get_updates_list(self):
        try:
            return json.loads(self.updates) if self.updates else []
        except:
            return []
    
    def set_updates_list(self, updates):
        self.updates = json.dumps(updates, ensure_ascii=False)
    
    @property
    def status_class(self):
        """Возвращает CSS класс для статуса"""
        status_map = {
            'planned': 'secondary',
            'active': 'success',
            'completed': 'info',
            'paused': 'warning'
        }
        return status_map.get(self.status, 'secondary')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'short_description': self.short_description,
            'description_full': self.description_full,
            'status': self.status,
            'status_name': self.status_name,
            'status_class': self.status_class,
            'mission_type': self.mission_type,
            'year': self.year,
            'goals': self.get_goals_list(),
            'partners': self.get_partners_list(),
            'updates': self.get_updates_list(),
            'sort_order': self.sort_order,
            'is_active': self.is_active
        }