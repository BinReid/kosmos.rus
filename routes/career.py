from flask import Blueprint, render_template, session, flash, redirect, url_for, request, abort
from models import db, User, University, CareerDirection, Vacancy
from forms import UniversityForm, CareerDirectionForm, VacancyForm
from utils.helpers import image_to_base64
from functools import wraps
from datetime import date

career_bp = Blueprint('career', __name__, url_prefix='/career')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def career_access_required(f):
    """Декоратор для проверки доступа к разделу Карьера (16+)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.has_career_access():
            flash('Раздел "Карьера" доступен только пользователям от 16 лет', 'warning')
            return redirect(url_for('profile.profile'))
        
        return f(*args, **kwargs)
    return decorated_function


def adult_required(f):
    """Декоратор для проверки доступа к вакансиям (18+)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_adult():
            flash('Раздел "Вакансии" доступен только пользователям от 18 лет', 'warning')
            return redirect(url_for('career.index'))
        
        return f(*args, **kwargs)
    return decorated_function


# ============ Пользовательские маршруты ============

@career_bp.route('/')
@career_access_required
def index():
    """Главная страница раздела Карьера"""
    user = User.query.get(session['user_id'])
    directions = CareerDirection.query.order_by(CareerDirection.sort_order).all()
    
    return render_template('career/index.html', 
                         user=user,
                         directions=directions,
                         show_vacancies=user.is_adult())


@career_bp.route('/directions/<int:direction_id>')
@career_access_required
def direction_detail(direction_id):
    """Детальная страница направления"""
    direction = CareerDirection.query.get_or_404(direction_id)
    user = User.query.get(session['user_id'])
    
    return render_template('career/direction_detail.html', 
                         direction=direction,
                         user=user)


@career_bp.route('/universities')
@career_access_required
def universities():
    """Список ВУЗов"""
    universities_list = University.query.order_by(University.name).all()
    user = User.query.get(session['user_id'])
    
    return render_template('career/universities.html', 
                         universities=universities_list,
                         user=user)


@career_bp.route('/universities/<int:university_id>')
@career_access_required
def university_detail(university_id):
    """Детальная страница ВУЗа"""
    university = University.query.get_or_404(university_id)
    user = User.query.get(session['user_id'])
    
    return render_template('career/university_detail.html', 
                         university=university,
                         user=user)


@career_bp.route('/vacancies')
@adult_required
def vacancies():
    """Список вакансий (только для 18+)"""
    vacancies_list = Vacancy.query.filter_by(is_active=True).order_by(Vacancy.created_at.desc()).all()
    user = User.query.get(session['user_id'])
    
    return render_template('career/vacancies.html', 
                         vacancies=vacancies_list,
                         user=user)


@career_bp.route('/vacancies/<int:vacancy_id>')
@adult_required
def vacancy_detail(vacancy_id):
    """Детальная страница вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    user = User.query.get(session['user_id'])
    
    if not vacancy.is_active:
        flash('Эта вакансия уже закрыта', 'warning')
        return redirect(url_for('career.vacancies'))
    
    return render_template('career/vacancy_detail.html', 
                         vacancy=vacancy,
                         user=user)