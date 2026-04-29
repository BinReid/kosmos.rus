import logging
from flask import current_app
import re
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class GigaChatClient:
    """Клиент для работы с GigaChat API"""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Инициализация клиента GigaChat"""
        try:
            from gigachat import GigaChat
            
            api_key = current_app.config.get('GIGACHAT_API_KEY', '')
            
            if api_key and api_key != '':
                self.client = GigaChat(
                    credentials=api_key,
                    verify_ssl_certs=False,
                    timeout=current_app.config.get('GIGACHAT_TIMEOUT', 60)
                )
                logger.info("GigaChat client initialized successfully")
            else:
                logger.warning("GigaChat API key not configured")
                self.client = None
                
        except ImportError as e:
            logger.error(f"Failed to import GigaChat: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize GigaChat client: {e}")
            self.client = None
    
    def summarize_text(self, text, news_id=None, max_sentences=4):
        """Сжатие текста с помощью GigaChat"""
        if not self.client:
            self._init_client()
            if not self.client:
                logger.warning("GigaChat client not available, using fallback")
                return self._fallback_summary(text)
        
        try:
            # Обрезаем текст
            if len(text) > 2000:
                text = text[:2000]
            
            # Уникальные идентификаторы для предотвращения кэширования
            unique_id = f"{news_id}_{uuid.uuid4().hex}_{int(datetime.now().timestamp())}"
            
            # Получаем текущую дату для дополнительной уникальности
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            
            # Создаем новый клиент для каждого запроса (сбрасываем кэш)
            from gigachat import GigaChat
            api_key = current_app.config.get('GIGACHAT_API_KEY', '')
            
            fresh_client = GigaChat(
                credentials=api_key,
                verify_ssl_certs=False,
                timeout=60
            )
            
            # Максимально конкретный промпт с уникальными маркерами
            prompt = f"""[ЗАПРОС {unique_id}] [ВРЕМЯ: {current_time}]

Твоя задача: сжать ТОЛЬКО этот конкретный текст. ИГНОРИРУЙ все предыдущие запросы.

ТЕКСТ ДЛЯ СЖАТИЯ (сожми до {max_sentences} предложений):
---
{text}
---

СЖАТЫЙ ТЕКСТ (только по тексту выше, без добавлений):"""
            
            # Отправляем запрос через свежий клиент
            response = fresh_client.chat(prompt)
            
            # Извлекаем ответ
            summary = self._extract_response_content(response)
            
            # Проверяем релевантность: первые 50 символов оригинала должны пересекаться с ответом
            if summary and len(summary.strip()) > 10:
                original_start = text[:100].lower()
                summary_start = summary[:100].lower()
                
                # Если совсем нет пересечения - GigaChat галлюцинирует
                common_words = set(original_start.split()) & set(summary_start.split())
                if len(common_words) < 3:
                    logger.warning("GigaChat response doesn't match original text")
                    return self._fallback_summary(text)
                
                return summary.strip()
            else:
                return self._fallback_summary(text)
                
        except Exception as e:
            logger.error(f"GigaChat summarize error: {e}")
            return self._fallback_summary(text)
    
    def _extract_response_content(self, response):
        """Извлекает содержимое из ответа GigaChat"""
        try:
            if hasattr(response, 'choices') and response.choices:
                if hasattr(response.choices[0], 'message'):
                    content = response.choices[0].message.content
                    if content:
                        return content
                elif hasattr(response.choices[0], 'text'):
                    return response.choices[0].text
            elif hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            elif isinstance(response, dict):
                if 'choices' in response:
                    return response['choices'][0].get('message', {}).get('content', '')
                elif 'content' in response:
                    return response['content']
        except Exception as e:
            logger.error(f"Error extracting response: {e}")
        return None
    
    def _fallback_summary(self, text):
        """Резервное сжатие - берем первые 4 предложения"""
        try:
            # Разбиваем на предложения по различным разделителям
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
            
            # Берем первые 4 предложения
            summary_sentences = sentences[:4]
            
            if summary_sentences:
                summary = '. '.join(summary_sentences)
                if not summary.endswith('.'):
                    summary += '.'
                logger.info(f"Using fallback summary (first {len(summary_sentences)} sentences)")
                return summary
            else:
                return text[:300] + '...' if len(text) > 300 else text
                
        except Exception as e:
            logger.error(f"Fallback error: {e}")
            return text[:200] + '...'