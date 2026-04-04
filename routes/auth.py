from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User
from forms import RegistrationForm, LoginForm
from utils.achievements import AchievementManager
from datetime import date
import hashlib

auth_bp = Blueprint('auth', __name__)

def generate_default_avatar(username, color):
    import base64
    initial = username[0].upper() if username else 'U'
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
        <rect width="100" height="100" fill="{color}" rx="50" ry="50"/>
        <text x="50" y="65" font-size="40" text-anchor="middle" fill="white" font-family="Arial">{initial}</text>
    </svg>'''
    
    return base64.b64encode(svg.encode()).decode()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Создаем пользователя
        user = User(
            username=form.username.data,
            email=form.email.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        
        # Генерируем аватар по умолчанию
        colors = ['#d32f2f', '#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#c2185b']
        color_index = int(hashlib.md5(user.username.encode()).hexdigest()[:2], 16) % len(colors)
        user.avatar_data = generate_default_avatar(user.username, colors[color_index])
        user.avatar_mime = 'image/svg+xml'
        
        db.session.add(user)
        db.session.commit()
        
        # Проверяем достижения
        AchievementManager.check_and_award(user, 'registration')
        
        session['user_id'] = user.id
        session['user_age'] = user.age
        
        # AJAX запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'redirect': url_for('profile.profile')
            })
        
        flash('Регистрация успешна! Добро пожаловать в Космос.Rus!', 'success')
        return redirect(url_for('profile.profile'))
    
    # Обработка ошибок валидации для AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0] if error_list else ''
        return jsonify({
            'success': False,
            'errors': errors
        })
    
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            # Обновляем streak
            today = date.today()
            if user.last_visit:
                if user.last_visit == today:
                    pass
                elif user.last_visit == today.replace(day=today.day - 1):
                    user.streak_days += 1
                else:
                    user.streak_days = 1
            else:
                user.streak_days = 1
            
            user.last_visit = today
            db.session.commit()
            
            # Проверяем достижения за серию
            AchievementManager.check_and_award(user, 'streak')
            
            session['user_id'] = user.id
            session['user_age'] = user.age
            session.permanent = form.remember_me.data
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'redirect': url_for('profile.profile')
                })
            
            flash(f'С возвращением, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('profile.profile'))
        
        # Неверные учетные данные
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': 'Неверное имя пользователя или пароль'
            })
        
        flash('Неверное имя пользователя или пароль', 'danger')
    
    # Обработка ошибок валидации для AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and form.errors:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = error_list[0] if error_list else ''
        return jsonify({
            'success': False,
            'errors': errors
        })
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Выход из системы"""
    session.pop('user_id', None)
    session.pop('user_age', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))