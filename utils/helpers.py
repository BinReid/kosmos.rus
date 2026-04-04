import base64
import json
from datetime import datetime, date
import re

def image_to_base64(file_data):
    """
    Конвертирует файл изображения в base64 строку
    Возвращает tuple (base64_data, mime_type)
    """
    if not file_data:
        return None, None
    
    # Определяем MIME тип
    content_type = file_data.content_type
    if not content_type:
        # Определяем по расширению файла
        filename = file_data.filename.lower()
        if filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.endswith('.gif'):
            content_type = 'image/gif'
        else:
            content_type = 'image/jpeg'
    
    # Читаем и кодируем
    data = file_data.read()
    base64_data = base64.b64encode(data).decode('utf-8')
    
    return base64_data, content_type

def base64_to_image(base64_data, mime_type):
    """Конвертирует base64 обратно в бинарные данные (для скачивания)"""
    if not base64_data:
        return None
    return base64.b64decode(base64_data)

def parse_options(options_json):
    """Парсит JSON с вариантами ответов"""
    try:
        return json.loads(options_json)
    except:
        return ['', '', '', '']

def serialize_options(options):
    """Сериализует варианты ответов в JSON"""
    return json.dumps(options, ensure_ascii=False)

def calculate_reading_time(text):
    """Расчет времени чтения статьи в минутах"""
    words_per_minute = 200
    words = len(text.split())
    minutes = max(1, int(words / words_per_minute))
    return minutes

def format_date(date_obj):
    """Форматирование даты"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%d.%m.%Y %H:%M')
    elif isinstance(date_obj, date):
        return date_obj.strftime('%d.%m.%Y')
    return str(date_obj)

def truncate_text(text, max_length=200):
    """Обрезка текста"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'

def slugify(text):
    """Создание URL-дружественной строки"""
    text = text.lower()
    text = re.sub(r'[^a-zа-я0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')