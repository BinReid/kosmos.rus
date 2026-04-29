// ========== ОРБИТАЛЬНОЕ МЕНЮ ==========
(function() {
    'use strict';
    
    const menuToggle = document.getElementById('menuToggle');
    const orbitItems = document.getElementById('orbitItems');
    
    let isMenuOpen = false;
    
    if (!menuToggle || !orbitItems) return;
    
    // Функция открытия меню
    function openMenu() {
        isMenuOpen = true;
        orbitItems.classList.add('active');
        menuToggle.classList.add('active');
    }
    
    // Функция закрытия меню
    function closeMenu() {
        isMenuOpen = false;
        orbitItems.classList.remove('active');
        menuToggle.classList.remove('active');
    }
    
    // Клик по центральной кнопке
    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        if (isMenuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });
    
    // Закрытие при клике вне меню
    document.addEventListener('click', (e) => {
        if (!isMenuOpen) return;
        const isMenuElement = menuToggle.contains(e.target) || orbitItems.contains(e.target);
        if (!isMenuElement) {
            closeMenu();
        }
    });
    
    // Закрытие по ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
            closeMenu();
        }
    });
    
    // Плавный переход по ссылкам
    const menuLinks = orbitItems.querySelectorAll('a');
    menuLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    closeMenu();
                    setTimeout(() => {
                        const headerOffset = 80;
                        const elementPosition = target.getBoundingClientRect().top;
                        window.scrollTo({
                            top: elementPosition + window.pageYOffset - headerOffset,
                            behavior: 'smooth'
                        });
                    }, 200);
                }
            }
        });
    });
    
    console.log('Орбитальное меню загружено');
})();