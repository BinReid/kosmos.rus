(function() {
    console.log('Auth.js loaded');

    // ========== ПЕРЕКЛЮЧЕНИЕ ВИДИМОСТИ ПАРОЛЯ ==========
    function initPasswordToggles() {
        console.log('Initializing password toggles...');
        
        // Находим все кнопки показа пароля
        const toggles = document.querySelectorAll('.password-toggle');
        console.log('Found password toggles:', toggles.length);
        
        toggles.forEach(btn => {
            // Удаляем старые обработчики, чтобы не было дублирования
            btn.removeEventListener('click', btn._listener);
            
            const handler = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Password toggle clicked');
                
                // Способ 1: через data-target (по ID)
                const targetId = this.getAttribute('data-target');
                let input = null;
                
                if (targetId) {
                    input = document.getElementById(targetId);
                    console.log('Looking by data-target:', targetId, 'found:', input);
                }
                
                // Способ 2: ищем ближайший input в группе
                if (!input) {
                    const parent = this.closest('.input-group, .password-group');
                    input = parent ? parent.querySelector('input[type="password"], input[type="text"]') : null;
                    console.log('Looking in parent group, found:', input);
                }
                
                // Способ 3: ищем предыдущий input
                if (!input) {
                    input = this.previousElementSibling;
                    while (input && input.tagName !== 'INPUT') {
                        input = input.previousElementSibling;
                    }
                    console.log('Looking as previous sibling, found:', input);
                }
                
                const icon = this.querySelector('i');
                
                if (input && icon) {
                    const currentType = input.getAttribute('type');
                    console.log('Current input type:', currentType);
                    
                    if (currentType === 'password') {
                        input.setAttribute('type', 'text');
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                        console.log('Changed to text');
                    } else {
                        input.setAttribute('type', 'password');
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                        console.log('Changed to password');
                    }
                } else {
                    console.error('Could not find input or icon:', {input, icon, btn: this});
                }
            };
            
            btn._listener = handler;
            btn.addEventListener('click', handler);
        });
    }

    // ========== ПРОВЕРКА СЛОЖНОСТИ ПАРОЛЯ ==========
    function checkPasswordStrength(password) {
        let score = 0;
        
        if (password.length >= 6) score++;
        if (password.length >= 10) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        const strengthLevels = ['Очень слабый', 'Слабый', 'Средний', 'Хороший', 'Отличный'];
        const strength = strengthLevels[Math.min(score, 4)];
        
        return { score: Math.min(score, 4), strength: strength };
    }

    // ========== ОБНОВЛЕНИЕ ИНДИКАТОРА СЛОЖНОСТИ ==========
    function updatePasswordStrength(passwordInput) {
        const password = passwordInput?.value || '';
        
        // Пытаемся найти элементы разными способами
        let strengthBar = document.querySelector('.strength-bar');
        let strengthText = document.querySelector('.strength-text');
        
        if (!strengthBar || !strengthText) {
            // Fallback для старой структуры
            strengthBar = document.querySelector('.strength-bar-fill')?.parentElement;
            strengthText = document.querySelector('.strength-text');
            if (strengthBar && strengthText) {
                // Для старой структуры используем прямой style
                const fill = strengthBar.querySelector('.strength-bar-fill');
                if (fill) {
                    const result = checkPasswordStrength(password);
                    const colors = ['#f44336', '#ff9800', '#ffc107', '#4caf50', '#4caf50'];
                    const width = (result.score / 4) * 100;
                    fill.style.width = width + '%';
                    fill.style.backgroundColor = colors[result.score];
                    strengthText.textContent = password.length ? result.strength : '';
                    strengthText.style.color = colors[result.score];
                }
                return;
            }
            return;
        }
        
        // Для новой структуры (как в settings.html)
        const result = checkPasswordStrength(password);
        const colors = ['#f44336', '#ff9800', '#ffc107', '#4caf50', '#4caf50'];
        const width = (result.score / 4) * 100;
        
        // Удаляем старый style если есть
        const oldStyle = document.getElementById('strength-dynamic-style');
        if (oldStyle) oldStyle.remove();
        
        // Создаем новый style
        const style = document.createElement('style');
        style.id = 'strength-dynamic-style';
        style.textContent = `.strength-bar::before { width: ${width}%; background: ${colors[result.score]}; }`;
        document.head.appendChild(style);
        
        strengthText.textContent = password.length ? result.strength : '';
        strengthText.style.color = colors[result.score];
    }

    // ========== ПРОВЕРКА СОВПАДЕНИЯ ПАРОЛЕЙ ==========
    function updatePasswordMatch(passwordInput, confirmInput, confirmErrorEl) {
        if (!passwordInput || !confirmInput || !confirmErrorEl) return;
        
        if (confirmInput.value.length === 0) {
            confirmErrorEl.style.display = 'none';
            return;
        }
        
        if (passwordInput.value === confirmInput.value) {
            confirmErrorEl.innerHTML = '<i class="fas fa-check-circle"></i> Пароли совпадают';
            confirmErrorEl.className = 'password-match match-success';
            confirmErrorEl.style.display = 'flex';
        } else {
            confirmErrorEl.innerHTML = '<i class="fas fa-exclamation-circle"></i> Пароли не совпадают';
            confirmErrorEl.className = 'password-match match-error';
            confirmErrorEl.style.display = 'flex';
        }
    }

    // ========== ИНИЦИАЛИЗАЦИЯ ФОРМЫ РЕГИСТРАЦИИ ==========
    function initRegisterForm() {
        const form = document.getElementById('registerForm');
        if (!form) {
            console.log('Register form not found');
            return false;
        }
        
        console.log('Initializing register form');
        
        // Элементы формы
        const username = document.getElementById('username');
        const email = document.getElementById('email');
        const age = document.getElementById('age');
        const password = document.getElementById('password');
        const confirm = document.getElementById('confirm_password');
        
        // Элементы для ошибок
        const usernameError = document.getElementById('usernameError');
        const emailError = document.getElementById('emailError');
        const ageError = document.getElementById('ageError');
        const passwordError = document.getElementById('passwordError');
        const confirmError = document.getElementById('confirmError');
        
        function validatePassword() {
            if (password.value.length > 0 && password.value.length < 6) {
                passwordError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Пароль должен быть не менее 6 символов';
                passwordError.style.display = 'flex';
                return false;
            } else {
                passwordError.style.display = 'none';
                return true;
            }
        }
        
        function validateConfirm() {
            if (confirm.value.length > 0) {
                if (password.value === confirm.value) {
                    confirmError.innerHTML = '<i class="fas fa-check-circle"></i> Пароли совпадают';
                    confirmError.className = 'password-match match-success';
                    confirmError.style.display = 'flex';
                    return true;
                } else {
                    confirmError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Пароли не совпадают';
                    confirmError.className = 'password-match match-error';
                    confirmError.style.display = 'flex';
                    return false;
                }
            } else {
                confirmError.style.display = 'none';
                return true;
            }
        }
        
        if (password) {
            password.addEventListener('input', function(e) {
                updatePasswordStrength(this);
                validatePassword();
                validateConfirm();
            });
            
            // Инициализация индикатора
            setTimeout(() => {
                updatePasswordStrength(password);
            }, 100);
        }
        
        if (confirm) {
            confirm.addEventListener('input', function() {
                validateConfirm();
            });
        }
        
        if (username) {
            username.addEventListener('input', () => {
                if (username.value.trim().length > 0 && username.value.trim().length < 3) {
                    usernameError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Имя пользователя должно быть не менее 3 символов';
                    usernameError.style.display = 'flex';
                } else {
                    usernameError.style.display = 'none';
                }
            });
        }
        
        if (email) {
            email.addEventListener('input', () => {
                const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (email.value.length > 0 && !regex.test(email.value)) {
                    emailError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Введите корректный email';
                    emailError.style.display = 'flex';
                } else {
                    emailError.style.display = 'none';
                }
            });
        }
        
        if (age) {
            age.addEventListener('input', () => {
                const val = parseInt(age.value);
                if (age.value.length > 0 && (isNaN(val) || val < 12 || val > 100)) {
                    ageError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Возраст должен быть от 12 до 100 лет';
                    ageError.style.display = 'flex';
                } else {
                    ageError.style.display = 'none';
                }
            });
        }
        
        let submitting = false;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (submitting) return;
            
            const terms = document.getElementById('terms');
            if (terms && !terms.checked) {
                const errorsDiv = document.getElementById('formErrors');
                errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Подтвердите согласие с условиями использования';
                errorsDiv.style.display = 'flex';
                return;
            }
            
            let isValid = true;
            
            if (username && username.value.trim().length < 3) {
                isValid = false;
                usernameError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Имя пользователя должно быть не менее 3 символов';
                usernameError.style.display = 'flex';
            }
            
            if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
                isValid = false;
                emailError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Введите корректный email';
                emailError.style.display = 'flex';
            }
            
            if (age) {
                const val = parseInt(age.value);
                if (isNaN(val) || val < 12 || val > 100) {
                    isValid = false;
                    ageError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Возраст должен быть от 12 до 100 лет';
                    ageError.style.display = 'flex';
                }
            }
            
            if (password && password.value.length < 6) {
                isValid = false;
                passwordError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Пароль должен быть не менее 6 символов';
                passwordError.style.display = 'flex';
            }
            
            if (confirm && confirm.value.length > 0 && password.value !== confirm.value) {
                isValid = false;
                confirmError.innerHTML = '<i class="fas fa-exclamation-circle"></i> Пароли не совпадают';
                confirmError.className = 'password-match match-error';
                confirmError.style.display = 'flex';
            }
            
            if (!isValid) return;
            
            const btn = document.getElementById('submitBtn');
            const errorsDiv = document.getElementById('formErrors');
            
            submitting = true;
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Регистрация...';
            errorsDiv.style.display = 'none';
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();
                
                if (data.success) {
                    if (window.starWelcome && data.username) {
                        await window.starWelcome.showWelcomeScreen(data.username);
                    }
                    window.location.href = data.redirect;
                } else {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-user-plus me-2"></i>Зарегистрироваться';
                    
                    let errorMsg = '';
                    if (data.errors) {
                        errorMsg = Object.values(data.errors).join('<br>');
                    } else if (data.error) {
                        errorMsg = data.error;
                    } else {
                        errorMsg = 'Ошибка при регистрации';
                    }
                    errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + errorMsg;
                    errorsDiv.style.display = 'flex';
                    submitting = false;
                }
            } catch (error) {
                console.error('Error:', error);
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-user-plus me-2"></i>Зарегистрироваться';
                errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Произошла ошибка. Попробуйте позже.';
                errorsDiv.style.display = 'flex';
                submitting = false;
            }
        });
        
        return true;
    }
    
    // ========== ИНИЦИАЛИЗАЦИЯ ФОРМЫ ВХОДА ==========
    function initLoginForm() {
        const form = document.getElementById('loginForm');
        if (!form) {
            console.log('Login form not found');
            return false;
        }
        
        console.log('Initializing login form');
        
        let submitting = false;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (submitting) return;
            
            const btn = document.getElementById('submitBtn');
            const errorsDiv = document.getElementById('formErrors');
            
            submitting = true;
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Вход...';
            errorsDiv.style.display = 'none';
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();
                
                if (data.success) {
                    if (window.starWelcome && data.username) {
                        await window.starWelcome.showWelcomeScreen(data.username);
                    }
                    window.location.href = data.redirect;
                } else {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Войти';
                    errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (data.error || 'Ошибка при входе');
                    errorsDiv.style.display = 'flex';
                    submitting = false;
                }
            } catch (error) {
                console.error('Error:', error);
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Войти';
                errorsDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Произошла ошибка. Попробуйте позже.';
                errorsDiv.style.display = 'flex';
                submitting = false;
            }
        });
        
        return true;
    }

    // ========== ЗАПУСК ПРИ ЗАГРУЗКЕ СТРАНИЦЫ ==========
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing auth forms...');
        
        initPasswordToggles();
        
        if (document.getElementById('registerForm')) {
            initRegisterForm();
        }
        
        if (document.getElementById('loginForm')) {
            initLoginForm();
        }
    });
})();