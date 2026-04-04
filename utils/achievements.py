from models import db, Achievement, UserAchievement
from flask import flash

class AchievementManager:
    """Менеджер достижений"""
    
    @staticmethod
    def init_achievements():
        """Инициализация стандартных достижений"""
        achievements = [
            Achievement(
                name='🚀 Первый шаг',
                description='Зарегистрироваться на платформе',
                icon='🚀',
                color='bronze',
                condition_type='registration',
                condition_value=1,
                points_reward=10
            ),
            Achievement(
                name='📚 Знаток космоса',
                description='Прочитать 5 новостей',
                icon='📚',
                color='bronze',
                condition_type='news_read',
                condition_value=5,
                points_reward=15
            ),
            Achievement(
                name='🎓 Эрудит',
                description='Прочитать 20 новостей',
                icon='🎓',
                color='silver',
                condition_type='news_read',
                condition_value=20,
                points_reward=30
            ),
            Achievement(
                name='🏆 Отличник',
                description='Пройти тест с результатом 80%+',
                icon='🏆',
                color='silver',
                condition_type='tests_passed',
                condition_value=1,
                points_reward=25
            ),
            Achievement(
                name='⭐ Звездный путь',
                description='Пройти 3 разных теста',
                icon='⭐',
                color='gold',
                condition_type='tests_passed',
                condition_value=3,
                points_reward=50
            ),
            Achievement(
                name='🔥 Серия побед',
                description='Заходить на сайт 3 дня подряд',
                icon='🔥',
                color='bronze',
                condition_type='streak',
                condition_value=3,
                points_reward=20
            ),
            Achievement(
                name='💪 Мастер космоса',
                description='Заходить на сайт 7 дней подряд',
                icon='💪',
                color='silver',
                condition_type='streak',
                condition_value=7,
                points_reward=50
            ),
            Achievement(
                name='🌟 Легенда космоса',
                description='Заходить на сайт 30 дней подряд',
                icon='🌟',
                color='gold',
                condition_type='streak',
                condition_value=30,
                points_reward=200
            ),
            Achievement(
                name='🎯 Любознательный',
                description='Правильно ответить на все вопросы теста',
                icon='🎯',
                color='gold',
                condition_type='perfect_test',
                condition_value=1,
                points_reward=100
            )
        ]
        
        for ach in achievements:
            if not Achievement.query.filter_by(name=ach.name).first():
                db.session.add(ach)
        db.session.commit()
    
    @staticmethod
    def check_and_award(user, action_type, value=1):
        """Проверка и выдача достижений"""
        from models import UserReadNews, TestResult
        
        awarded = []
        
        # Поиск достижений по типу
        achievements = Achievement.query.filter_by(condition_type=action_type).all()
        
        for achievement in achievements:
            # Проверяем, есть ли уже такое достижение
            existing = UserAchievement.query.filter_by(
                user_id=user.id,
                achievement_id=achievement.id
            ).first()
            
            if existing:
                continue
            
            condition_met = False
            
            if action_type == 'registration':
                condition_met = True
            
            elif action_type == 'news_read':
                count = UserReadNews.query.filter_by(user_id=user.id).count()
                condition_met = count >= achievement.condition_value
            
            elif action_type == 'tests_passed':
                count = TestResult.query.filter_by(user_id=user.id).count()
                condition_met = count >= achievement.condition_value
            
            elif action_type == 'streak':
                condition_met = user.streak_days >= achievement.condition_value
            
            elif action_type == 'perfect_test':
                condition_met = value == 100  # 100% правильных ответов
            
            if condition_met:
                user_ach = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id
                )
                db.session.add(user_ach)
                user.points += achievement.points_reward
                awarded.append(achievement)
                
                flash(f'🎉 Получено достижение: {achievement.name}! +{achievement.points_reward} очков', 'success')
        
        if awarded:
            AchievementManager._update_level(user)
            db.session.commit()
        
        return awarded
    
    @staticmethod
    def _update_level(user):
        """Обновление уровня пользователя"""
        from config import Config
        
        for level, points_needed in Config.LEVELS.items():
            if user.points >= points_needed:
                user.level = level
            else:
                break
        
        if user.level == 5:
            # Максимальный уровень
            pass
    
    @staticmethod
    def get_user_achievements(user):
        """Получить все достижения пользователя"""
        return UserAchievement.query.filter_by(user_id=user.id).all()
    
    @staticmethod
    def get_available_achievements():
        """Получить все возможные достижения"""
        return Achievement.query.all()