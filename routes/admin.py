from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, News, Test, Question, DailyFact, Achievement, University, CareerDirection, Vacancy, Project
from forms import NewsForm, TestForm, FactForm, AchievementForm, UniversityForm, CareerDirectionForm, VacancyForm, ProjectForm
from utils.achievements import AchievementManager
from utils.helpers import image_to_base64
import json
from functools import wraps
from datetime import *

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Декоратор проверки прав администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Доступ запрещен. Требуются права администратора.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    from datetime import date, timedelta
    from models import DailyFact
    
    daily_fact = DailyFact.query.order_by(DailyFact.date.desc()).first()

    stats = {
        'users_count': User.query.count(),
        'news_count': News.query.count(),
        'tests_count': Test.query.count(),
        'achievements_count': Achievement.query.count(),
        'projects_count': Project.query.count(),
        'universities_count': University.query.count(),
        'directions_count': CareerDirection.query.count(),
        'vacancies_count': Vacancy.query.count(),
        'active_today': User.query.filter(User.last_visit == date.today()).count(),
        'active_week': User.query.filter(User.last_visit >= date.today() - timedelta(days=7)).count(),
        'total_views': News.query.with_entities(db.func.sum(News.views)).scalar() or 0,
        'weekly_activity': [
            User.query.filter(User.last_visit == date.today() - timedelta(days=6)).count(),
            User.query.filter(User.last_visit == date.today() - timedelta(days=5)).count(),
            User.query.filter(User.last_visit == date.today() - timedelta(days=4)).count(),
            User.query.filter(User.last_visit == date.today() - timedelta(days=3)).count(),
            User.query.filter(User.last_visit == date.today() - timedelta(days=2)).count(),
            User.query.filter(User.last_visit == date.today() - timedelta(days=1)).count(),
            User.query.filter(User.last_visit == date.today()).count(),
        ],
    }
    
    recent_news = News.query.order_by(News.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    daily_fact = DailyFact.query.order_by(DailyFact.date.desc()).first()

    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_news=recent_news,
                         fact=daily_fact,
                         recent_users=recent_users)


@admin_bp.route('/news')
@admin_required
def news():
    """Управление новостями"""
    news_list = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news.html', news=news_list)


@admin_bp.route('/news/add', methods=['GET', 'POST'])
@admin_required
def news_add():
    """Добавление новости"""
    form = NewsForm()
    
    if form.validate_on_submit():
        news = News(
            title=form.title.data,
            content=form.content.data
        )
        
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                news.image_data = base64_data
                news.image_mime = mime_type
        
        db.session.add(news)
        db.session.commit()
        
        flash('Новость добавлена успешно!', 'success')
        return redirect(url_for('admin.news'))
    
    return render_template('admin/news_add.html', form=form)


@admin_bp.route('/news/edit/<int:news_id>', methods=['GET', 'POST'])
@admin_required
def news_edit(news_id):
    """Редактирование новости"""
    news = News.query.get_or_404(news_id)
    form = NewsForm(obj=news)
    
    if form.validate_on_submit():
        news.title = form.title.data
        news.content = form.content.data
        
        if form.remove_image.data == '1':
            news.image_data = None
            news.image_mime = None
            flash('Изображение удалено', 'info')
        
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                news.image_data = base64_data
                news.image_mime = mime_type
                flash('Изображение обновлено', 'success')
        
        db.session.commit()
        flash('Новость обновлена успешно!', 'success')
        return redirect(url_for('admin.news'))
    
    return render_template('admin/news_edit.html', news=news, form=form)


@admin_bp.route('/news/delete/<int:news_id>')
@admin_required
def news_delete(news_id):
    """Удаление новости"""
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    flash('Новость удалена', 'success')
    return redirect(url_for('admin.news'))


@admin_bp.route('/tests')
@admin_required
def tests():
    """Управление тестами"""
    tests_list = Test.query.all()
    return render_template('admin/tests.html', tests=tests_list)


@admin_bp.route('/tests/add', methods=['GET', 'POST'])
@admin_required
def tests_add():
    """Добавление теста"""
    form = TestForm()
    
    if form.validate_on_submit():
        test = Test(
            title=form.title.data,
            description=form.description.data
        )
        db.session.add(test)
        db.session.commit()
        
        question_count = int(request.form.get('question_count', 0))
        for i in range(question_count):
            question_text = request.form.get(f'question_{i}', '').strip()
            if question_text:
                options = [
                    request.form.get(f'q{i}_opt1', '').strip(),
                    request.form.get(f'q{i}_opt2', '').strip(),
                    request.form.get(f'q{i}_opt3', '').strip(),
                    request.form.get(f'q{i}_opt4', '').strip()
                ]
                correct = int(request.form.get(f'q{i}_correct', 1)) - 1
                
                question = Question(
                    test_id=test.id,
                    text=question_text,
                    options=json.dumps(options, ensure_ascii=False),
                    correct=correct
                )
                db.session.add(question)
        
        db.session.commit()
        flash('Тест добавлен успешно!', 'success')
        return redirect(url_for('admin.tests'))
    
    return render_template('admin/tests_add.html', form=form)


@admin_bp.route('/tests/edit/<int:test_id>', methods=['GET', 'POST'])
@admin_required
def tests_edit(test_id):
    """Редактирование теста"""
    test = Test.query.get_or_404(test_id)
    form = TestForm(obj=test)
    
    if form.validate_on_submit():
        test.title = form.title.data
        test.description = form.description.data
        db.session.commit()
        flash('Тест обновлен', 'success')
        return redirect(url_for('admin.tests'))
    
    return render_template('admin/tests_edit.html', test=test, form=form)


@admin_bp.route('/tests/delete/<int:test_id>')
@admin_required
def tests_delete(test_id):
    """Удаление теста"""
    test = Test.query.get_or_404(test_id)
    db.session.delete(test)
    db.session.commit()
    flash('Тест удален', 'success')
    return redirect(url_for('admin.tests'))


@admin_bp.route('/fact', methods=['GET', 'POST'])
@admin_required
def fact():
    """Редактирование факта дня"""
    from datetime import date
    
    fact_obj = DailyFact.query.order_by(DailyFact.date.desc()).first()
    form = FactForm(obj=fact_obj)
    
    if form.validate_on_submit():
        if fact_obj:
            fact_obj.fact = form.fact.data
            fact_obj.date = date.today()
        else:
            fact_obj = DailyFact(
                fact=form.fact.data,
                date=date.today()
            )
            db.session.add(fact_obj)
        
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                fact_obj.image_data = base64_data
                fact_obj.image_mime = mime_type
        
        db.session.commit()
        flash('Факт дня обновлен!', 'success')
        return redirect(url_for('admin.fact'))
    
    return render_template('admin/fact.html', fact=fact_obj, form=form)


@admin_bp.route('/users')
@admin_required
def users():
    """Управление пользователями"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    users_list = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin/users.html', users=users_list)


@admin_bp.route('/users/toggle_admin/<int:user_id>')
@admin_required
def users_toggle_admin(user_id):
    """Переключение прав администратора"""
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        flash('Нельзя изменить свои права администратора', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'администратором' if user.is_admin else 'обычным пользователем'
        flash(f'Пользователь {user.username} теперь {status}', 'success')
    return redirect(url_for('admin.users'))


# ============ Управление достижениями ============

@admin_bp.route('/achievements')
@admin_required
def achievements():
    """Управление достижениями"""
    achievements_list = Achievement.query.order_by(Achievement.id).all()
    return render_template('admin/achievements.html', achievements=achievements_list)


@admin_bp.route('/achievements/add', methods=['GET', 'POST'])
@admin_required
def achievement_add():
    """Добавление достижения"""
    form = AchievementForm()
    
    if form.validate_on_submit():
        achievement = Achievement(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data,
            color=form.color.data,
            condition_type=form.condition_type.data,
            condition_value=form.condition_value.data,
            points_reward=form.points_reward.data
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        flash(f'Достижение "{achievement.name}" успешно добавлено!', 'success')
        return redirect(url_for('admin.achievements'))
    
    return render_template('admin/achievement_add.html', form=form)


@admin_bp.route('/achievements/edit/<int:achievement_id>', methods=['GET', 'POST'])
@admin_required
def achievement_edit(achievement_id):
    """Редактирование достижения"""
    achievement = Achievement.query.get_or_404(achievement_id)
    form = AchievementForm(obj=achievement)
    
    if form.validate_on_submit():
        achievement.name = form.name.data
        achievement.description = form.description.data
        achievement.icon = form.icon.data
        achievement.color = form.color.data
        achievement.condition_type = form.condition_type.data
        achievement.condition_value = form.condition_value.data
        achievement.points_reward = form.points_reward.data
        
        db.session.commit()
        
        flash(f'Достижение "{achievement.name}" успешно обновлено!', 'success')
        return redirect(url_for('admin.achievements'))
    
    return render_template('admin/achievement_edit.html', form=form, achievement=achievement)


@admin_bp.route('/achievements/delete/<int:achievement_id>')
@admin_required
def achievement_delete(achievement_id):
    """Удаление достижения"""
    achievement = Achievement.query.get_or_404(achievement_id)
    
    # Проверяем, есть ли пользователи с этим достижением
    from models import UserAchievement
    users_with_achievement = UserAchievement.query.filter_by(achievement_id=achievement_id).count()
    
    if users_with_achievement > 0:
        flash(f'Невозможно удалить достижение "{achievement.name}", так как {users_with_achievement} пользователей уже получили его.', 'danger')
    else:
        name = achievement.name
        db.session.delete(achievement)
        db.session.commit()
        flash(f'Достижение "{name}" удалено', 'success')
    
    return redirect(url_for('admin.achievements'))


# ============ Управление ВУЗами ============

@admin_bp.route('/universities')
@admin_required
def admin_universities():
    """Управление ВУЗами"""
    universities_list = University.query.order_by(University.name).all()
    return render_template('admin/universities.html', universities=universities_list)


@admin_bp.route('/universities/add', methods=['GET', 'POST'])
@admin_required
def admin_university_add():
    """Добавление ВУЗа"""
    form = UniversityForm()
    
    if form.validate_on_submit():
        # Преобразуем специальности в JSON
        specialties = [s.strip() for s in form.specialties.data.split('\n') if s.strip()]
        
        university = University(
            name=form.name.data,
            description=form.description.data,
            city=form.city.data,
            website=form.website.data,
            specialties=json.dumps(specialties, ensure_ascii=False)
        )
        
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                university.image_data = base64_data
                university.image_mime = mime_type
        
        db.session.add(university)
        db.session.commit()
        
        flash('ВУЗ успешно добавлен!', 'success')
        return redirect(url_for('admin.admin_universities'))
    
    return render_template('admin/university_add.html', form=form)


@admin_bp.route('/universities/edit/<int:university_id>', methods=['GET', 'POST'])
@admin_required
def admin_university_edit(university_id):
    """Редактирование ВУЗа"""
    university = University.query.get_or_404(university_id)
    form = UniversityForm(obj=university)
    
    if form.validate_on_submit():
        university.name = form.name.data
        university.description = form.description.data
        university.city = form.city.data
        university.website = form.website.data
        
        specialties = [s.strip() for s in form.specialties.data.split('\n') if s.strip()]
        university.specialties = json.dumps(specialties, ensure_ascii=False)
        
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                university.image_data = base64_data
                university.image_mime = mime_type
        
        db.session.commit()
        flash('ВУЗ успешно обновлен!', 'success')
        return redirect(url_for('admin.admin_universities'))
    
    # Заполняем поле specialties
    specialties_list = university.get_specialties_list()
    form.specialties.data = '\n'.join(specialties_list)
    
    return render_template('admin/university_edit.html', form=form, university=university)


@admin_bp.route('/universities/delete/<int:university_id>')
@admin_required
def admin_university_delete(university_id):
    """Удаление ВУЗа"""
    university = University.query.get_or_404(university_id)
    db.session.delete(university)
    db.session.commit()
    flash('ВУЗ удален', 'success')
    return redirect(url_for('admin.admin_universities'))


# ============ Управление направлениями карьеры ============

@admin_bp.route('/directions')
@admin_required
def admin_directions():
    """Управление направлениями карьеры"""
    directions = CareerDirection.query.order_by(CareerDirection.sort_order).all()
    return render_template('admin/directions.html', directions=directions)


@admin_bp.route('/directions/add', methods=['GET', 'POST'])
@admin_required
def admin_direction_add():
    """Добавление направления"""
    form = CareerDirectionForm()
    
    if form.validate_on_submit():
        direction = CareerDirection(
            title=form.title.data,
            description=form.description.data,
            icon=form.icon.data,
            content=form.content.data,
            sort_order=form.sort_order.data or 0
        )
        db.session.add(direction)
        db.session.commit()
        flash('Направление успешно добавлено!', 'success')
        return redirect(url_for('admin.admin_directions'))
    
    return render_template('admin/direction_add.html', form=form)


@admin_bp.route('/directions/edit/<int:direction_id>', methods=['GET', 'POST'])
@admin_required
def admin_direction_edit(direction_id):
    """Редактирование направления"""
    direction = CareerDirection.query.get_or_404(direction_id)
    form = CareerDirectionForm(obj=direction)
    
    if form.validate_on_submit():
        direction.title = form.title.data
        direction.description = form.description.data
        direction.icon = form.icon.data
        direction.content = form.content.data
        direction.sort_order = form.sort_order.data or 0
        db.session.commit()
        flash('Направление успешно обновлено!', 'success')
        return redirect(url_for('admin.admin_directions'))
    
    return render_template('admin/direction_edit.html', form=form, direction=direction)


@admin_bp.route('/directions/delete/<int:direction_id>')
@admin_required
def admin_direction_delete(direction_id):
    """Удаление направления"""
    direction = CareerDirection.query.get_or_404(direction_id)
    db.session.delete(direction)
    db.session.commit()
    flash('Направление удалено', 'success')
    return redirect(url_for('admin.admin_directions'))


# ============ Управление вакансиями ============

@admin_bp.route('/vacancies')
@admin_required
def admin_vacancies():
    """Управление вакансиями"""
    vacancies_list = Vacancy.query.order_by(Vacancy.created_at.desc()).all()
    return render_template('admin/vacancies.html', vacancies=vacancies_list)


@admin_bp.route('/vacancies/add', methods=['GET', 'POST'])
@admin_required
def admin_vacancy_add():
    """Добавление вакансии"""
    form = VacancyForm()
    
    if form.validate_on_submit():
        vacancy = Vacancy(
            title=form.title.data,
            company=form.company.data,
            description=form.description.data,
            requirements=form.requirements.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            location=form.location.data,
            contact_email=form.contact_email.data,
            is_active=form.is_active.data,
            expires_at=form.expires_at.data
        )
        db.session.add(vacancy)
        db.session.commit()
        flash('Вакансия успешно добавлена!', 'success')
        return redirect(url_for('admin.admin_vacancies'))
    
    return render_template('admin/vacancy_add.html', form=form)


@admin_bp.route('/vacancies/edit/<int:vacancy_id>', methods=['GET', 'POST'])
@admin_required
def admin_vacancy_edit(vacancy_id):
    """Редактирование вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    form = VacancyForm(obj=vacancy)
    
    if form.validate_on_submit():
        vacancy.title = form.title.data
        vacancy.company = form.company.data
        vacancy.description = form.description.data
        vacancy.requirements = form.requirements.data
        vacancy.salary_min = form.salary_min.data
        vacancy.salary_max = form.salary_max.data
        vacancy.location = form.location.data
        vacancy.contact_email = form.contact_email.data
        vacancy.is_active = form.is_active.data
        vacancy.expires_at = form.expires_at.data
        db.session.commit()
        flash('Вакансия успешно обновлена!', 'success')
        return redirect(url_for('admin.admin_vacancies'))
    
    return render_template('admin/vacancy_edit.html', form=form, vacancy=vacancy)


@admin_bp.route('/vacancies/delete/<int:vacancy_id>')
@admin_required
def admin_vacancy_delete(vacancy_id):
    """Удаление вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    db.session.delete(vacancy)
    db.session.commit()
    flash('Вакансия удалена', 'success')
    return redirect(url_for('admin.admin_vacancies'))


# ============ API для вопросов ============

@admin_bp.route('/api/questions/delete/<int:question_id>', methods=['POST'])
@admin_required
def api_delete_question(question_id):
    """API для удаления вопроса"""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Вопрос удален'})


@admin_bp.route('/api/tests/<int:test_id>/questions/delete_all', methods=['POST'])
@admin_required
def api_delete_all_questions(test_id):
    """API для удаления всех вопросов теста"""
    test = Test.query.get_or_404(test_id)
    Question.query.filter_by(test_id=test_id).delete()
    db.session.commit()
    return jsonify({'success': True, 'message': f'Все вопросы теста "{test.title}" удалены'})


@admin_bp.route('/api/questions/edit/<int:question_id>', methods=['POST'])
@admin_required
def api_edit_question(question_id):
    """API для редактирования вопроса"""
    try:
        question = Question.query.get_or_404(question_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Нет данных'}), 400
        
        if 'text' in data:
            question.text = data['text']
        
        options = [
            data.get('option1', ''),
            data.get('option2', ''),
            data.get('option3', ''),
            data.get('option4', '')
        ]
        question.options = json.dumps(options, ensure_ascii=False)
        
        if 'correct' in data:
            question.correct = data['correct'] - 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Вопрос обновлен'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/tests/<int:test_id>/questions/add', methods=['POST'])
@admin_required
def api_add_question(test_id):
    """API для добавления вопроса в тест"""
    try:
        test = Test.query.get_or_404(test_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Нет данных'}), 400
        
        options = [
            data.get('option1', ''),
            data.get('option2', ''),
            data.get('option3', ''),
            data.get('option4', '')
        ]
        
        question = Question(
            test_id=test.id,
            text=data.get('text', ''),
            options=json.dumps(options, ensure_ascii=False),
            correct=data.get('correct', 1) - 1
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Вопрос добавлен', 'question_id': question.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@admin_bp.route('/projects')
@admin_required
def admin_projects():
    """Управление проектами"""
    projects_list = Project.query.order_by(Project.sort_order, Project.created_at.desc()).all()
    return render_template('admin/projects.html', projects=projects_list)


@admin_bp.route('/projects/add', methods=['GET', 'POST'])
@admin_required
def admin_project_add():
    """Добавление проекта"""
    form = ProjectForm()
    
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            short_description=form.short_description.data,
            description_full=form.description_full.data,
            status=form.status.data,
            mission_type=form.mission_type.data,
            year=form.year.data,
            sort_order=form.sort_order.data or 0,
            is_active=form.is_active.data
        )
        
        # Устанавливаем название статуса для отображения
        status_names = {
            'planned': 'В плане',
            'active': 'Активен',
            'completed': 'Завершён',
            'paused': 'Приостановлен'
        }
        project.status_name = status_names.get(form.status.data, 'В плане')
        
        # Обработка целей
        if form.goals.data:
            goals = [g.strip() for g in form.goals.data.split('\n') if g.strip()]
            project.set_goals_list(goals)
        
        # Обработка партнёров
        if form.partners.data:
            partners = [p.strip() for p in form.partners.data.split('\n') if p.strip()]
            project.set_partners_list(partners)
        
        # Обработка хронологии
        if form.updates.data:
            updates = []
            for line in form.updates.data.split('\n'):
                if '|' in line:
                    date_part, text_part = line.split('|', 1)
                    updates.append({
                        'date': date_part.strip(),
                        'text': text_part.strip()
                    })
                elif line.strip():
                    updates.append({
                        'date': '',
                        'text': line.strip()
                    })
            project.set_updates_list(updates)
        
        # Обработка изображения
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                project.image_data = base64_data
                project.image_mime = mime_type
        
        db.session.add(project)
        db.session.commit()
        
        flash(f'Проект "{project.title}" успешно добавлен!', 'success')
        return redirect(url_for('admin.admin_projects'))
    
    return render_template('admin/project_add.html', form=form)

@admin_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def admin_project_edit(project_id):
    """Редактирование проекта"""
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.short_description = form.short_description.data
        project.description_full = form.description_full.data
        project.status = form.status.data
        project.mission_type = form.mission_type.data
        project.year = form.year.data
        project.sort_order = form.sort_order.data or 0
        project.is_active = form.is_active.data
        
        # Обновляем название статуса
        status_names = {
            'planned': 'В плане',
            'active': 'Активен',
            'completed': 'Завершён',
            'paused': 'Приостановлен'
        }
        project.status_name = status_names.get(form.status.data, 'В плане')
        
        # Обработка целей
        if form.goals.data:
            goals = [g.strip() for g in form.goals.data.split('\n') if g.strip()]
            project.set_goals_list(goals)
        else:
            project.set_goals_list([])
        
        # Обработка партнёров
        if form.partners.data:
            partners = [p.strip() for p in form.partners.data.split('\n') if p.strip()]
            project.set_partners_list(partners)
        else:
            project.set_partners_list([])
        
        # Обработка хронологии
        if form.updates.data:
            updates = []
            for line in form.updates.data.split('\n'):
                if '|' in line:
                    date_part, text_part = line.split('|', 1)
                    updates.append({
                        'date': date_part.strip(),
                        'text': text_part.strip()
                    })
                elif line.strip():
                    updates.append({
                        'date': '',
                        'text': line.strip()
                    })
            project.set_updates_list(updates)
        else:
            project.set_updates_list([])
        
        # Удаление изображения
        if form.remove_image.data == '1':
            project.image_data = None
            project.image_mime = None
            flash('Изображение удалено', 'info')
        
        # Обработка нового изображения
        if form.image.data and form.image.data.filename:
            base64_data, mime_type = image_to_base64(form.image.data)
            if base64_data:
                project.image_data = base64_data
                project.image_mime = mime_type
                flash('Изображение обновлено', 'success')
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Проект "{project.title}" успешно обновлён!', 'success')
        return redirect(url_for('admin.admin_projects'))
    
    # Заполняем поля формы текущими данными
    form.goals.data = '\n'.join(project.get_goals_list())
    form.partners.data = '\n'.join(project.get_partners_list())
    
    updates_lines = []
    for update in project.get_updates_list():
        if update.get('date'):
            updates_lines.append(f"{update['date']} | {update['text']}")
        else:
            updates_lines.append(update['text'])
    form.updates.data = '\n'.join(updates_lines)
    
    return render_template('admin/project_edit.html', form=form, project=project)


@admin_bp.route('/projects/delete/<int:project_id>')
@admin_required
def admin_project_delete(project_id):
    """Удаление проекта"""
    project = Project.query.get_or_404(project_id)
    title = project.title
    db.session.delete(project)
    db.session.commit()
    flash(f'Проект "{title}" удалён', 'success')
    return redirect(url_for('admin.admin_projects'))


@admin_bp.route('/projects/toggle/<int:project_id>')
@admin_required
def admin_project_toggle(project_id):
    """Включение/выключение отображения проекта"""
    project = Project.query.get_or_404(project_id)
    project.is_active = not project.is_active
    db.session.commit()
    status = 'активен' if project.is_active else 'скрыт'
    flash(f'Проект "{project.title}" теперь {status}', 'success')
    return redirect(url_for('admin.admin_projects'))