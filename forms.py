from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, IntegerField, SelectField, PasswordField, BooleanField, HiddenField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
import json


class NewsForm(FlaskForm):
    """Форма для создания/редактирования новости"""
    title = StringField('Заголовок', validators=[
        DataRequired(message='Заголовок обязателен'),
        Length(min=3, max=200, message='Заголовок должен быть от 3 до 200 символов')
    ])
    content = TextAreaField('Содержание', validators=[
        DataRequired(message='Содержание обязательно'),
        Length(min=10, message='Содержание должно быть не менее 10 символов')
    ])
    image = FileField('Изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Разрешены только изображения!'),
        Optional()
    ])
    remove_image = HiddenField('Удалить изображение', default='0')


class TestForm(FlaskForm):
    """Форма для создания теста"""
    title = StringField('Название теста', validators=[
        DataRequired(message='Название обязательно'),
        Length(min=3, max=200, message='Название должно быть от 3 до 200 символов')
    ])
    description = TextAreaField('Описание', validators=[
        Length(max=500, message='Описание не должно превышать 500 символов'),
        Optional()
    ])


class QuestionForm(FlaskForm):
    """Форма для вопроса (динамическая)"""
    text = StringField('Текст вопроса', validators=[
        DataRequired(message='Текст вопроса обязателен'),
        Length(min=5, max=500, message='Вопрос должен быть от 5 до 500 символов')
    ])
    option1 = StringField('Вариант 1', validators=[DataRequired(message='Вариант ответа обязателен')])
    option2 = StringField('Вариант 2', validators=[DataRequired(message='Вариант ответа обязателен')])
    option3 = StringField('Вариант 3', validators=[DataRequired(message='Вариант ответа обязателен')])
    option4 = StringField('Вариант 4', validators=[DataRequired(message='Вариант ответа обязателен')])
    correct = IntegerField('Правильный ответ', validators=[
        DataRequired(message='Укажите правильный ответ'),
        NumberRange(min=1, max=4, message='Правильный ответ должен быть от 1 до 4')
    ])


class RegistrationForm(FlaskForm):
    """Форма регистрации с возрастом"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=3, max=80, message='Имя пользователя должно быть от 3 до 80 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес'),
        Length(max=120)
    ])
    age = IntegerField('Возраст', validators=[
        DataRequired(message='Укажите ваш возраст'),
        NumberRange(min=12, max=100, message='Возраст должен быть от 12 лет')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_password = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])
    
    def validate_username(self, field):
        from models import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Имя пользователя уже занято')
    
    def validate_email(self, field):
        from models import User
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email уже зарегистрирован')


class LoginForm(FlaskForm):
    """Форма входа"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен')
    ])
    remember_me = BooleanField('Запомнить меня')


class ProfileSettingsForm(FlaskForm):
    """Форма настроек профиля"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Имя пользователя обязательно'),
        Length(min=3, max=80, message='Имя пользователя должно быть от 3 до 80 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес'),
        Length(max=120)
    ])
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Разрешены только изображения!'),
        Optional()
    ])
    remove_avatar = HiddenField('Удалить аватар', default='0')
    
    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(ProfileSettingsForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, field):
        if field.data == self.original_username:
            return
        from models import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Имя пользователя уже занято')
    
    def validate_email(self, field):
        if field.data == self.original_email:
            return
        from models import User
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email уже зарегистрирован')


class PasswordChangeForm(FlaskForm):
    """Форма смены пароля"""
    current_password = PasswordField('Текущий пароль', validators=[
        DataRequired(message='Введите текущий пароль')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Введите новый пароль'),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_new_password = PasswordField('Подтверждение нового пароля', validators=[
        DataRequired(message='Подтвердите новый пароль'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])


class FactForm(FlaskForm):
    """Форма для факта дня"""
    fact = TextAreaField('Факт дня', validators=[
        DataRequired(message='Факт обязателен'),
        Length(min=10, max=500, message='Факт должен быть от 10 до 500 символов')
    ])
    image = FileField('Изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Разрешены только изображения!'),
        Optional()
    ])


class AchievementForm(FlaskForm):
    """Форма для создания/редактирования достижения"""
    name = StringField('Название', validators=[
        DataRequired(message='Название обязательно'),
        Length(min=3, max=100, message='Название должно быть от 3 до 100 символов')
    ])
    description = StringField('Описание', validators=[
        DataRequired(message='Описание обязательно'),
        Length(max=200, message='Описание не должно превышать 200 символов')
    ])
    icon = StringField('Иконка (эмодзи)', validators=[
        DataRequired(message='Иконка обязательна'),
        Length(max=10, message='Иконка должна быть короткой')
    ])
    color = SelectField('Цвет', choices=[
        ('bronze', 'Бронзовый'),
        ('silver', 'Серебряный'),
        ('gold', 'Золотой'),
        ('platinum', 'Платиновый')
    ], default='bronze')
    condition_type = SelectField('Тип условия', choices=[
        ('registration', 'Регистрация'),
        ('news_read', 'Чтение новостей'),
        ('tests_passed', 'Прохождение тестов'),
        ('streak', 'Серия посещений'),
        ('perfect_test', 'Идеальный тест')
    ], default='registration')
    condition_value = IntegerField('Значение условия', validators=[
        DataRequired(message='Значение обязательно'),
        NumberRange(min=1, max=100, message='Значение должно быть от 1 до 100')
    ], default=1)
    points_reward = IntegerField('Награда в очках', validators=[
        DataRequired(message='Награда обязательна'),
        NumberRange(min=5, max=500, message='Награда должна быть от 5 до 500 очков')
    ], default=10)


class SearchForm(FlaskForm):
    """Форма поиска"""
    query = StringField('Поиск', validators=[
        DataRequired(message='Введите поисковый запрос'),
        Length(min=2, max=100, message='Запрос должен быть от 2 до 100 символов')
    ])
    search_type = SelectField('Тип поиска', choices=[
        ('news', 'Новости'),
        ('tests', 'Тесты'),
        ('users', 'Пользователи')
    ], default='news')


# ============ Формы для раздела Карьера ============

class UniversityForm(FlaskForm):
    """Форма для ВУЗа"""
    name = StringField('Название ВУЗа', validators=[
        DataRequired(message='Название обязательно'),
        Length(min=3, max=200, message='Название должно быть от 3 до 200 символов')
    ])
    description = TextAreaField('Описание', validators=[
        DataRequired(message='Описание обязательно'),
        Length(min=20, message='Описание должно быть не менее 20 символов')
    ])
    city = StringField('Город', validators=[
        DataRequired(message='Город обязателен'),
        Length(max=100)
    ])
    website = StringField('Сайт', validators=[
        Optional(),
        Length(max=200)
    ])
    specialties = TextAreaField('Специальности (каждая с новой строки)', validators=[
        DataRequired(message='Укажите специальности')
    ])
    image = FileField('Изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Разрешены только изображения!'),
        Optional()
    ])


class CareerDirectionForm(FlaskForm):
    """Форма для направления карьеры"""
    title = StringField('Название направления', validators=[
        DataRequired(message='Название обязательно'),
        Length(min=3, max=200)
    ])
    description = TextAreaField('Краткое описание', validators=[
        DataRequired(message='Описание обязательно'),
        Length(min=10, max=300)
    ])
    icon = StringField('Иконка (эмодзи)', validators=[
        DataRequired(message='Иконка обязательна'),
        Length(max=10)
    ])
    content = TextAreaField('Полное содержание', validators=[
        DataRequired(message='Содержание обязательно'),
        Length(min=50)
    ])
    sort_order = IntegerField('Порядок сортировки', validators=[
        Optional(),
        NumberRange(min=0)
    ], default=0)


class VacancyForm(FlaskForm):
    """Форма для вакансии"""
    title = StringField('Название вакансии', validators=[
        DataRequired(message='Название обязательно'),
        Length(min=3, max=200)
    ])
    company = StringField('Компания/Организация', validators=[
        DataRequired(message='Компания обязательна'),
        Length(min=2, max=200)
    ])
    description = TextAreaField('Описание вакансии', validators=[
        DataRequired(message='Описание обязательно'),
        Length(min=20)
    ])
    requirements = TextAreaField('Требования', validators=[
        DataRequired(message='Требования обязательны'),
        Length(min=20)
    ])
    salary_min = IntegerField('Зарплата от', validators=[
        Optional(),
        NumberRange(min=0)
    ])
    salary_max = IntegerField('Зарплата до', validators=[
        Optional(),
        NumberRange(min=0)
    ])
    location = StringField('Местоположение', validators=[
        DataRequired(message='Местоположение обязательно'),
        Length(max=200)
    ])
    contact_email = StringField('Email для отклика', validators=[
        Optional(),
        Email(message='Введите корректный email')
    ])
    is_active = BooleanField('Активна', default=True)
    expires_at = DateField('Дата истечения', validators=[
        Optional()
    ], format='%Y-%m-%d')