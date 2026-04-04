// star-welcome.js
const starWelcome = {
    showWelcomeScreen(username) {
        return new Promise((resolve) => {
            const hour = new Date().getHours();
            let greetingText = '';
            
            if (hour >= 5 && hour < 12) {
                greetingText = `ДОБРОЕ УТРО, ${username.toUpperCase()}`;
            } else if (hour >= 12 && hour < 17) {
                greetingText = `ДОБРЫЙ ДЕНЬ, ${username.toUpperCase()}`;
            } else if (hour >= 17 && hour < 22) {
                greetingText = `ДОБРЫЙ ВЕЧЕР, ${username.toUpperCase()}`;
            } else {
                greetingText = `ДОБРОЙ НОЧИ, ${username.toUpperCase()}`;
            }
            
            // Создаем overlay
            const overlay = document.createElement('div');
            overlay.id = 'welcomeOverlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(ellipse at center, #0a0f2a 0%, #03030a 100%);
                z-index: 999999;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
                opacity: 1;
                transition: opacity 0.5s ease;
            `;
            
            overlay.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <h1 style="font-family: 'Russo One', cursive; font-size: 2.5rem; letter-spacing: 6px; color: white; margin-bottom: 20px; text-shadow: 0 0 30px rgba(255,255,255,0.3);">${greetingText}</h1>
                    <p style="font-size: 1.2rem; color: rgba(255,255,255,0.7);">Добро пожаловать в Космос.Rus</p>
                    <div style="display: flex; justify-content: center; gap: 12px; margin-top: 40px;">
                        <span style="width: 10px; height: 10px; background: white; border-radius: 50%; animation: dotPulse 1.4s ease-in-out infinite;"></span>
                        <span style="width: 10px; height: 10px; background: white; border-radius: 50%; animation: dotPulse 1.4s ease-in-out infinite 0.2s;"></span>
                        <span style="width: 10px; height: 10px; background: white; border-radius: 50%; animation: dotPulse 1.4s ease-in-out infinite 0.4s;"></span>
                    </div>
                </div>
                <style>
                    @keyframes dotPulse {
                        0%, 60%, 100% { transform: scale(1); opacity: 0.5; }
                        30% { transform: scale(1.5); opacity: 1; }
                    }
                </style>
            `;
            
            document.body.appendChild(overlay);
            document.body.style.overflow = 'hidden';
            
            // Показываем 2.5 секунды
            setTimeout(() => {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    if (overlay && overlay.remove) {
                        overlay.remove();
                    }
                    document.body.style.overflow = '';
                    resolve();
                }, 500);
            }, 2500);
        });
    }
};

window.starWelcome = starWelcome;