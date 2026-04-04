from flask import Blueprint, render_template, request, jsonify, current_app, session
from models import db, News, DailyFact, UserReadNews, User
from utils.helpers import format_date, truncate_text
from utils.gigachat_client import GigaChatClient
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Главная страница"""
    news_list = News.query.order_by(News.created_at.desc()).limit(5).all()
    daily_fact = DailyFact.query.order_by(DailyFact.date.desc()).first()
    
    # Если нет факта дня - создаем
    if not daily_fact:
        from datetime import date
        facts = [
            "Первый искусственный спутник Земли был запущен СССР 4 октября 1957 года.",
            "Юрий Гагарин стал первым человеком в космосе 12 апреля 1961 года.",
            "Валентина Терешкова - первая женщина-космонавт, совершившая полёт в 1963 году.",
            "Алексей Леонов - первый человек, вышедший в открытый космос (18 марта 1965 года).",
            "Станция «Мир» проработала на орбите 15 лет - с 1986 по 2001 год.",
            "Ракета-носитель «Ангара» - первая российская ракета, разработанная после распада СССР.",
            "Космодром «Восточный» - первый гражданский космодром России, открытый в 2016 году."
        ]
        import random
        fact_text = random.choice(facts)
        daily_fact = DailyFact(fact=fact_text, date=date.today())
        db.session.add(daily_fact)
        db.session.commit()
    
    # Статистика для главной страницы
    stats = {
        'total_news': News.query.count(),
        'total_launches': '3000+',
        'cosmonauts': '120+',
        'satellites': '160+'
    }
    
    return render_template('index.html', 
                         news=news_list, 
                         fact=daily_fact,
                         stats=stats)

@main_bp.route('/news')
def news_list():
    """Список новостей"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('NEWS_PER_PAGE', 10)
    
    news_all = News.query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('news.html', news=news_all)

@main_bp.route('/product')
def product():
    """О продукте"""
    return render_template('product.html')

@main_bp.route('/news/<int:news_id>')
def news_detail(news_id):
    """Детальная страница новости"""
    from utils.achievements import AchievementManager
    
    news = News.query.get_or_404(news_id)
    
    # Проверяем, смотрел ли пользователь эту новость
    user_viewed = False
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            # Проверяем, есть ли запись о просмотре
            existing_view = UserReadNews.query.filter_by(
                user_id=user.id, news_id=news_id
            ).first()
            
            if not existing_view:
                # Записываем просмотр
                read = UserReadNews(user_id=user.id, news_id=news_id)
                db.session.add(read)
                # Увеличиваем счетчик просмотров только если это первый просмотр
                news.views += 1
                db.session.commit()
                
                # Проверяем достижения за чтение новостей
                AchievementManager.check_and_award(user, 'news_read')
            else:
                # Пользователь уже смотрел, но счетчик не увеличиваем
                user_viewed = True
                db.session.commit()
    else:
        # Для неавторизованных пользователей - увеличиваем счетчик
        # Но используем сессию, чтобы не накручивать просмотры
        viewed_news = session.get('viewed_news', [])
        if news_id not in viewed_news:
            news.views += 1
            viewed_news.append(news_id)
            session['viewed_news'] = viewed_news
            db.session.commit()
    
    return render_template('news_detail.html', news=news)

@main_bp.route('/api/summarize/<int:news_id>', methods=['POST'])
def summarize_news(news_id):
    """API для сжатия новости через GigaChat"""
    try:
        news = News.query.get_or_404(news_id)
        
        # Инициализируем клиент GigaChat
        giga = GigaChatClient()
        
        # Передаем news_id для уникальности запроса
        summary = giga.summarize_text(news.content, news_id=news_id, max_sentences=4)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        current_app.logger.error(f"Error summarizing news {news_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500