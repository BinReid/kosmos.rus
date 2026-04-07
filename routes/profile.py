from flask import Blueprint, render_template, session, flash, redirect, url_for, request, current_app
from models import db, User, TestResult
from utils.achievements import AchievementManager
from forms import ProfileSettingsForm, PasswordChangeForm
from config import Config
from datetime import date
from functools import wraps

profile_bp = Blueprint('profile', __name__)

def login_required(f):
    """Декоратор проверки авторизации"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@profile_bp.route('/profile')
@login_required
def profile():
    """Личный кабинет пользователя"""
    user = User.query.get(session['user_id'])
    
    # Обновляем данные в сессии
    session['is_admin'] = user.is_admin
    session['user_age'] = user.age
    
    # Обновляем серию посещений
    today = date.today()
    if user.last_visit:
        if user.last_visit < today:
            if user.last_visit == today.replace(day=today.day - 1):
                user.streak_days += 1
            else:
                user.streak_days = 1
            user.last_visit = today
            db.session.commit()
            
            # Проверяем достижения
            AchievementManager.check_and_award(user, 'streak')
    
    # Получаем достижения пользователя
    user_achievements = AchievementManager.get_user_achievements(user)
    
    # Получаем результаты тестов
    test_results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.passed_at.desc()).all()
    
    # Вычисляем прогресс до следующего уровня
    points_to_next = 0
    progress = 0
    
    for level, points_needed in Config.LEVELS.items():
        if user.level == level:
            next_level = level + 1
            if next_level in Config.LEVELS:
                points_to_next = Config.LEVELS[next_level] - user.points
                current_level_points = Config.LEVELS[level]
                level_range = Config.LEVELS[next_level] - current_level_points
                progress = ((user.points - current_level_points) / level_range) * 100 if level_range > 0 else 100
            else:
                progress = 100
            break
    
    # Статистика
    stats = {
        'total_read': len(user.read_news.all()),
        'total_tests': len(test_results),
        'best_score': max([r.percentage for r in test_results]) if test_results else 0,
        'total_points': user.points
    }
    
    return render_template('profile.html', 
                         user=user, 
                         achievements=user_achievements,
                         test_results=test_results,
                         points_to_next=points_to_next,
                         progress=progress,
                         stats=stats)


@profile_bp.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Настройки профиля"""
    user = User.query.get(session['user_id'])
    
    form = ProfileSettingsForm(
        original_username=user.username,
        original_email=user.email,
        obj=user
    )
    password_form = PasswordChangeForm()
    
    if request.method == 'POST':
        if 'update_profile' in request.form:
            # Обновление профиля
            if form.validate_on_submit():
                user.username = form.username.data
                user.email = form.email.data

                # Удаление аватара
                if request.form.get('remove_avatar_checkbox') == '1':
                    user.avatar_data = None
                    user.avatar_mime = None
                    flash('Аватар удален', 'info')
                                
                # Загрузка нового аватара
                if form.avatar.data and form.avatar.data.filename:
                    from utils.helpers import image_to_base64
                    base64_data, mime_type = image_to_base64(form.avatar.data)
                    if base64_data:
                        user.avatar_data = base64_data
                        user.avatar_mime = mime_type
                        flash('Аватар обновлен', 'success')
                
                db.session.commit()
                # Обновляем сессию
                session['user_age'] = user.age
                flash('Настройки профиля обновлены!', 'success')
                return redirect(url_for('profile.settings'))
        
        elif 'change_password' in request.form:
            # Смена пароля
            if password_form.validate_on_submit():
                if user.check_password(password_form.current_password.data):
                    user.set_password(password_form.new_password.data)
                    db.session.commit()
                    flash('Пароль успешно изменен!', 'success')
                    return redirect(url_for('profile.settings'))
                else:
                    flash('Текущий пароль введен неверно', 'danger')
    
    return render_template('settings.html', user=user, form=form, password_form=password_form)