// ========== УПРАВЛЕНИЕ ПРЕЛОАДЕРОМ (ТОЛЬКО ПРИ ПЕРВОЙ ЗАГРУЗКЕ) ==========
(function() {
    const loader = document.getElementById('loader');
    const contentWrapper = document.getElementById('contentWrapper');
    
    // Проверяем, загружался ли уже сайт в этой вкладке
    const hasLoadedBefore = sessionStorage.getItem('cosmos_loaded');
    
    if (hasLoadedBefore) {
        // Если уже загружался - сразу прячем прелоадер и показываем контент
        if (loader) {
            loader.classList.add('force-hidden');
        }
        if (contentWrapper) {
            contentWrapper.classList.add('visible');
        }
        document.body.style.overflow = 'auto';
    } else {
        // Первая загрузка - показываем прелоадер с анимацией
        if (loader) {
            // Убираем force-hidden, если был
            loader.classList.remove('force-hidden');
            loader.classList.remove('hidden');
            
            // Запускаем анимацию загрузки
            setTimeout(() => {
                loader.style.opacity = '0';
                setTimeout(() => {
                    loader.classList.add('hidden');
                    if (contentWrapper) {
                        contentWrapper.classList.add('visible');
                    }
                    document.body.style.overflow = 'auto';
                    // Сохраняем флаг, что сайт уже загружен
                    sessionStorage.setItem('cosmos_loaded', 'true');
                }, 800);
            }, 2800); // Время анимации прелоадера
            
            // Блокируем скролл пока грузится прелоадер
            document.body.style.overflow = 'hidden';
        } else {
            // Если прелоадера нет - просто показываем контент
            if (contentWrapper) {
                contentWrapper.classList.add('visible');
            }
            document.body.style.overflow = 'auto';
            sessionStorage.setItem('cosmos_loaded', 'true');
        }
    }
})();

// ========== УЛУЧШЕННЫЕ FLASH УВЕДОМЛЕНИЯ С ПРОГРЕСС-ПОЛОСКОЙ ==========
class NotificationManager {
    constructor() {
        this.container = null;
        this.defaultDuration = 5000; // 5 секунд по умолчанию
        this.initContainer();
    }

    initContainer() {
        // Создаем контейнер для уведомлений, если его нет
        if (!document.getElementById('flashContainer')) {
            this.container = document.createElement('div');
            this.container.id = 'flashContainer';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('flashContainer');
        }
    }

    show(message, type = 'info', duration = this.defaultDuration) {
        const notification = document.createElement('div');
        notification.className = `flash-message flash-${type} alert alert-${type}`;
        
        // Выбираем иконку в зависимости от типа
        let iconClass = 'fa-info-circle';
        if (type === 'success') iconClass = 'fa-check-circle';
        if (type === 'danger' || type === 'error') iconClass = 'fa-exclamation-triangle';
        if (type === 'warning') iconClass = 'fa-exclamation-circle';
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="notification-text">${this.escapeHtml(message)}</div>
                <button class="notification-close" aria-label="Закрыть">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-progress">
                <div class="progress-bar-animated"></div>
            </div>
        `;
        
        this.container.appendChild(notification);
        
        // Получаем элементы
        const closeBtn = notification.querySelector('.notification-close');
        const progressBar = notification.querySelector('.progress-bar-animated');
        
        // Устанавливаем начальную ширину
        progressBar.style.width = '100%';
        
        // Запускаем анимацию прогресс-полоски
        setTimeout(() => {
            progressBar.style.transition = `width ${duration}ms linear`;
            progressBar.style.width = '0%';
        }, 50);
        
        // Функция закрытия
        const closeNotification = () => {
            if (notification.classList.contains('hiding')) return;
            notification.classList.add('hiding');
            setTimeout(() => {
                if (notification && notification.remove) notification.remove();
            }, 200);
        };
        
        // Закрытие по кнопке
        closeBtn.addEventListener('click', closeNotification);
        
        // Автоматическое закрытие через duration
        const timeoutId = setTimeout(closeNotification, duration);
        
        // При наведении мыши останавливаем таймер и прогресс
        notification.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
            // Получаем текущую ширину
            const computedStyle = getComputedStyle(progressBar);
            const currentWidth = parseFloat(computedStyle.width);
            const parentWidth = parseFloat(computedStyle.parentElement?.width || progressBar.parentElement?.offsetWidth);
            const remainingPercent = currentWidth / parentWidth;
            
            // Сохраняем оставшееся время
            notification._remainingTime = duration * remainingPercent;
            
            // Останавливаем анимацию
            progressBar.style.transition = 'none';
            progressBar.style.width = `${currentWidth}px`;
        });
        
        // При уходе мыши возобновляем с оставшимся временем
        notification.addEventListener('mouseleave', () => {
            const remainingTime = notification._remainingTime || duration;
            
            if (remainingTime > 100) {
                const newTimeoutId = setTimeout(closeNotification, remainingTime);
                notification._timeoutId = newTimeoutId;
                
                // Возобновляем анимацию прогресса
                progressBar.style.transition = `width ${remainingTime}ms linear`;
                setTimeout(() => {
                    progressBar.style.width = '0%';
                }, 10);
            } else if (remainingTime > 0) {
                closeNotification();
            }
        });
        
        notification._timeoutId = timeoutId;
        
        return notification;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration) {
        return this.show(message, 'danger', duration);
    }
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }
}

// Инициализируем менеджер уведомлений
const notificationManager = new NotificationManager();

// Переопределяем глобальную функцию showNotification
window.showNotification = function(message, type = 'info', duration = 5000) {
    return notificationManager.show(message, type, duration);
};

// ========== ПЛАВНАЯ ПРОКРУТКА ПО ЯКОРЯМ ==========
document.addEventListener('DOMContentLoaded', () => {
    // Обработка существующих flash-сообщений от сервера
    const existingFlashMessages = document.querySelectorAll('.flash-message.global-flash, .alert.global-flash, .flash-message:not(#flashContainer .flash-message), .alert:not(#flashContainer .alert)');
    existingFlashMessages.forEach(msg => {
        // Получаем тип и текст
        let type = 'info';
        if (msg.classList.contains('alert-success') || msg.classList.contains('flash-success')) type = 'success';
        if (msg.classList.contains('alert-danger') || msg.classList.contains('flash-danger')) type = 'danger';
        if (msg.classList.contains('alert-warning') || msg.classList.contains('flash-warning')) type = 'warning';
        
        const messageText = msg.textContent?.trim();
        if (messageText && messageText !== '') {
            // Создаем красивое уведомление
            notificationManager.show(messageText, type);
        }
        // Удаляем оригинальное сообщение
        msg.remove();
    });
    
    // Плавная прокрутка по якорям
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                e.preventDefault();
                
                // Закрываем орбитальное меню, если открыто
                const orbitItems = document.getElementById('orbitItems');
                const menuToggle = document.getElementById('menuToggle');
                if (orbitItems && orbitItems.classList.contains('active')) {
                    orbitItems.classList.remove('active');
                    const label = menuToggle?.querySelector('.menu-label');
                    if (label) label.textContent = 'МЕНЮ';
                }
                
                const target = document.querySelector(targetId);
                if (target) {
                    const headerOffset = 80;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // ========== АНИМАЦИЯ ПОЯВЛЕНИЯ ПРИ СКРОЛЛЕ ==========
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .glass-card, .timeline-item, .cosmos-card, .achievement-card, .vacancy-card, .university-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(25px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // ========== ЗВЁЗДНЫЙ ФОН (дополнительная анимация) ==========
    function createStars() {
        // Проверяем, не созданы ли уже звёзды
        if (document.querySelectorAll('.dynamic-star').length > 50) return;
        
        const starCount = 100;
        const body = document.body;
        for (let i = 0; i < starCount; i++) {
            const star = document.createElement('div');
            star.className = 'star dynamic-star';
            const size = Math.random() * 3 + 1;
            star.style.width = size + 'px';
            star.style.height = size + 'px';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = Math.random() * 5 + 's';
            star.style.animationDuration = Math.random() * 3 + 2 + 's';
            star.style.position = 'fixed';
            star.style.background = 'white';
            star.style.borderRadius = '50%';
            star.style.pointerEvents = 'none';
            star.style.zIndex = '1';
            star.style.opacity = Math.random() * 0.7 + 0.3;
            body.appendChild(star);
        }
    }
    
    // Создаём звёзды только на главной странице
    if (window.location.pathname === '/' || window.location.pathname === '/index' || window.location.pathname === '') {
        createStars();
    }

    // ========== TOOLTIPS ==========
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
    }
    
    // ========== ПЕРЕХВАТ КЛИКОВ ПО ССЫЛКАМ ДЛЯ ПЛАВНОЙ ЗАГРУЗКИ ==========
    document.querySelectorAll('a:not([href^="#"]):not([target="_blank"])').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.hasAttribute('data-no-pjax') && !this.hasAttribute('download')) {
                // Сохраняем флаг, что это переход внутри сайта
                sessionStorage.setItem('cosmos_navigating', 'true');
            }
        });
    });
    
    // ========== ПОДСВЕТКА АКТИВНОГО ПУНКТА МЕНЮ ==========
    function highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const menuLinks = document.querySelectorAll('.orbit-items a, .navbar-nav a');
        
        menuLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '#' && href !== '') {
                // Убираем домен из href если есть
                let linkPath = href.replace(window.location.origin, '');
                // Сравниваем пути
                if (linkPath === currentPath || 
                    (linkPath !== '/' && currentPath.startsWith(linkPath)) ||
                    (linkPath === '/' && currentPath === '/')) {
                    link.style.color = 'var(--russia-red)';
                    if (link.parentElement) {
                        link.parentElement.classList.add('active');
                    }
                }
            }
        });
    }
    
    highlightCurrentPage();
});

// ========== ГЛОБАЛЬНЫЕ ФУНКЦИИ ==========

// Функция для копирования текста
window.copyToClipboard = async function(text, successMessage = 'Скопировано!') {
    try {
        await navigator.clipboard.writeText(text);
        notificationManager.success(successMessage);
        return true;
    } catch (err) {
        console.error('Ошибка копирования:', err);
        notificationManager.error('Не удалось скопировать');
        return false;
    }
};

// Плавная загрузка страниц
window.navigateTo = function(url, event) {
    if (event) event.preventDefault();
    
    // Показываем мини-прелоадер
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(3, 3, 10, 0.9);
        z-index: 10001;
        display: flex;
        justify-content: center;
        align-items: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    `;
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div style="width: 50px; height: 50px; border: 3px solid var(--russia-red); border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 20px;"></div>
            <p style="color: white; font-family: 'Russo One', cursive;">ЗАГРУЗКА...</p>
        </div>
    `;
    document.body.appendChild(overlay);
    
    setTimeout(() => overlay.style.opacity = '1', 10);
    
    setTimeout(() => {
        window.location.href = url;
    }, 300);
};

// Принудительный сброс прелоадера
window.resetLoaderState = function() {
    sessionStorage.removeItem('cosmos_loaded');
    location.reload();
};

// Добавляем анимацию спиннера в head если её нет
if (!document.querySelector('#loader-spinner-style')) {
    const spinnerStyle = document.createElement('style');
    spinnerStyle.id = 'loader-spinner-style';
    spinnerStyle.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(spinnerStyle);
}

// ========== ОБРАБОТКА AJAX ЗАПРОСОВ С УВЕДОМЛЕНИЯМИ ==========
window.ajaxWithNotification = async function(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (data.message) {
            const type = data.status === 'success' ? 'success' : 
                        data.status === 'error' ? 'danger' : 'info';
            notificationManager.show(data.message, type);
        }
        
        return data;
    } catch (error) {
        console.error('AJAX Error:', error);
        notificationManager.error('Произошла ошибка при выполнении запроса');
        throw error;
    }
};

// Экспортируем для использования в других скриптах
window.notificationManager = notificationManager;