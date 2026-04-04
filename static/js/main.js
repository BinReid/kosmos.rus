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

// ========== ОРБИТАЛЬНОЕ МЕНЮ (ЦУП) ==========
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const orbitItems = document.getElementById('orbitItems');
    let isMenuOpen = false;

    if (menuToggle && orbitItems) {
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            isMenuOpen = !isMenuOpen;
            orbitItems.classList.toggle('active');
            
            const label = menuToggle.querySelector('.menu-label');
            if (label) {
                label.innerText = isMenuOpen ? '✕' : 'ЦУП';
            }
        });
    }

    // Закрытие меню при клике вне его
    document.addEventListener('click', (e) => {
        if (isMenuOpen && menuToggle && !menuToggle.contains(e.target) && !orbitItems?.contains(e.target)) {
            orbitItems.classList.remove('active');
            isMenuOpen = false;
            const label = menuToggle.querySelector('.menu-label');
            if (label) label.innerText = 'ЦУП';
        }
    });

    // ========== ПЛАВНАЯ ПРОКРУТКА ПО ЯКОРЯМ ==========
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                e.preventDefault();
                
                // Закрываем орбитальное меню, если открыто
                if (orbitItems && orbitItems.classList.contains('active')) {
                    orbitItems.classList.remove('active');
                    isMenuOpen = false;
                    const label = menuToggle?.querySelector('.menu-label');
                    if (label) label.innerText = 'ЦУП';
                }
                
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
    
    document.querySelectorAll('.card, .glass-card, .timeline-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(25px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // ========== ЗВЁЗДНЫЙ ФОН (дополнительная анимация) ==========
    function createStars() {
        // Проверяем, не созданы ли уже звёзды
        if (document.querySelectorAll('.star').length > 0) return;
        
        const starCount = 80;
        const body = document.body;
        for (let i = 0; i < starCount; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            const size = Math.random() * 3 + 1;
            star.style.width = size + 'px';
            star.style.height = size + 'px';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = Math.random() * 5 + 's';
            star.style.animationDuration = Math.random() * 3 + 2 + 's';
            body.appendChild(star);
        }
    }
    
    // Создаём звёзды только на главной странице
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        createStars();
    }

    // ========== TOOLTIPS ==========
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));
    
    // ========== ПЕРЕХВАТ КЛИКОВ ПО ССЫЛКАМ ДЛЯ ПЛАВНОЙ ЗАГРУЗКИ ==========
    // Делаем навигацию без перезагрузки страницы (опционально)
    // Но оставляем стандартное поведение для обычных ссылок
    document.querySelectorAll('a:not([href^="#"]):not([target="_blank"])').forEach(link => {
        // Добавляем класс для отслеживания переходов
        link.addEventListener('click', function(e) {
            // Не перехватываем если есть атрибут data-no-pjax или это внешняя ссылка
            if (this.hasAttribute('data-no-pjax')) return;
            
            // Сохраняем флаг, что это переход внутри сайта
            sessionStorage.setItem('cosmos_navigating', 'true');
        });
    });
});

// ========== ГЛОБАЛЬНЫЕ ФУНКЦИИ ==========
window.showNotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.background = 'rgba(10, 15, 42, 0.95)';
    notification.style.backdropFilter = 'blur(12px)';
    notification.style.border = '1px solid var(--russia-red)';
    notification.style.color = 'white';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
};

// ========== ПРИНУДИТЕЛЬНЫЙ СБРОС ПРЕЛОАДЕРА (если нужно показать снова) ==========
window.resetLoaderState = function() {
    sessionStorage.removeItem('cosmos_loaded');
    location.reload();
};