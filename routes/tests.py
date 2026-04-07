from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Test, TestResult, Question, User
from utils.achievements import AchievementManager
import json
from functools import wraps

tests_bp = Blueprint('tests', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@tests_bp.route('/tests')
@login_required
def tests():
    """Список тестов"""
    tests_list = Test.query.all()
    user_results = TestResult.query.filter_by(user_id=session['user_id']).all()
    passed_tests = [r.test_id for r in user_results]
    
    return render_template('tests.html', tests=tests_list, passed_tests=passed_tests)

@tests_bp.route('/test/<int:test_id>')
@login_required
def test_detail(test_id):
    """Страница прохождения теста"""
    test = Test.query.get_or_404(test_id)
    
    # Проверяем, проходил ли пользователь этот тест
    passed = TestResult.query.filter_by(
        user_id=session['user_id'], 
        test_id=test_id
    ).first()
    
    if passed:
        flash('Вы уже проходили этот тест!', 'info')
        return redirect(url_for('tests.tests'))
    
    return render_template('test_detail.html', test=test)

@tests_bp.route('/test/<int:test_id>/submit', methods=['POST'])
@login_required
def test_submit(test_id):
    """Сохранение результатов теста"""
    test = Test.query.get_or_404(test_id)
    user = User.query.get(session['user_id'])
    questions = test.questions.all()
    
    score = 0
    for i, question in enumerate(questions):
        answer = request.form.get(f'q{i}')
        if answer and int(answer) - 1 == question.correct:
            score += 1
    
    max_score = len(questions)
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    
    # Сохраняем результат
    result = TestResult(
        user_id=user.id,
        test_id=test_id,
        score=score,
        max_score=max_score,
        percentage=percentage
    )
    db.session.add(result)
    
    # Начисляем очки
    points_earned = score * 5
    user.points += points_earned
    db.session.commit()
    
    # Проверяем достижения
    AchievementManager.check_and_award(user, 'tests_passed')
    
    # Проверяем достижения за результат теста
    if percentage >= 80:
        AchievementManager.check_and_award(user, 'test_passed_80', 80)

    # Проверяем на идеальный результат (100%)
    if percentage == 100:
        AchievementManager.check_and_award(user, 'perfect_test', 100)
        
    # Обновляем уровень
    AchievementManager._update_level(user)
    db.session.commit()
    
    flash(f'Тест завершен! Результат: {score}/{max_score} ({percentage:.0f}%)', 'success')
    
    return redirect(url_for('tests.tests'))

@tests_bp.route('/api/tests/results')
@login_required
def get_test_results():
    """API для получения результатов тестов (для AJAX)"""
    user = User.query.get(session['user_id'])
    results = TestResult.query.filter_by(user_id=user.id).all()
    
    data = [{
        'test_id': r.test_id,
        'score': r.score,
        'max_score': r.max_score,
        'percentage': r.percentage,
        'passed_at': r.passed_at.strftime('%d.%m.%Y')
    } for r in results]
    
    return jsonify(data)