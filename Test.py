<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Logger Bot</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 100%;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 16px;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        }

        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }

        .main-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            flex: 1;
        }

        .section {
            margin-bottom: 25px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-title::before {
            content: '';
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 2px;
        }

        .toggle-group {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .toggle-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            transition: background 0.3s ease;
        }

        .toggle-item:hover {
            background: #e9ecef;
        }

        .toggle-label {
            font-size: 16px;
            color: #333;
            font-weight: 500;
        }

        .toggle-switch {
            position: relative;
            width: 50px;
            height: 26px;
            background: #ccc;
            border-radius: 13px;
            cursor: pointer;
            transition: background 0.3s ease;
        }

        .toggle-switch.active {
            background: #667eea;
        }

        .toggle-switch::after {
            content: '';
            position: absolute;
            top: 3px;
            left: 3px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: transform 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }

        .toggle-switch.active::after {
            transform: translateX(24px);
        }

        .action-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 20px;
        }

        .btn {
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: #f8f9fa;
            color: #333;
            border: 2px solid #e9ecef;
        }

        .btn-secondary:hover {
            background: #e9ecef;
        }

        .btn-danger {
            background: #dc3545;
            color: white;
        }

        .btn-danger:hover {
            background: #c82333;
            transform: translateY(-2px);
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-online {
            background: #28a745;
            animation: pulse 2s infinite;
        }

        .status-offline {
            background: #dc3545;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: white;
        }

        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .message {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }

        .message-title {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .message-text {
            color: #666;
            font-size: 14px;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            color: white;
            opacity: 0.8;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Business Logger</h1>
            <p>Панель управления ботом</p>
        </div>

        <div id="loading" class="loading">
            <div class="spinner"></div>
            <p>Загрузка данных...</p>
        </div>

        <div id="content" style="display: none;">
            <!-- Статистика -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="messages-count">0</div>
                    <div class="stat-label">Сообщений</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="view-once-count">0</div>
                    <div class="stat-label">View Once</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="deleted-count">0</div>
                    <div class="stat-label">Удалено</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="edited-count">0</div>
                    <div class="stat-label">Изменено</div>
                </div>
            </div>

            <!-- Главная панель -->
            <div class="main-card">
                <!-- Статус подключения -->
                <div class="section">
                    <div class="section-title">Статус подключения</div>
                    <div id="connection-status">
                        <div class="message">
                            <div class="message-title">
                                <span class="status-indicator status-offline"></span>
                                Проверка подключения...
                            </div>
                            <div class="message-text">Ожидание данных от бота</div>
                        </div>
                    </div>
                </div>

                <!-- Настройки -->
                <div class="section">
                    <div class="section-title">Настройки уведомлений</div>
                    <div class="toggle-group">
                        <div class="toggle-item">
                            <span class="toggle-label">Показывать свои сообщения</span>
                            <div class="toggle-switch" id="show-own-messages" data-setting="show_own_messages"></div>
                        </div>
                        <div class="toggle-item">
                            <span class="toggle-label">Уведомлять об изменениях</span>
                            <div class="toggle-switch" id="notify-edits" data-setting="notify_edits"></div>
                        </div>
                        <div class="toggle-item">
                            <span class="toggle-label">Уведомлять об удалениях</span>
                            <div class="toggle-switch" id="notify-deletes" data-setting="notify_deletes"></div>
                        </div>
                        <div class="toggle-item">
                            <span class="toggle-label">Уведомлять о View Once</span>
                            <div class="toggle-switch" id="notify-view-once" data-setting="notify_view_once"></div>
                        </div>
                    </div>
                </div>

                <!-- Кнопки действий -->
                <div class="section">
                    <div class="section-title">Действия</div>
                    <div class="action-buttons">
                        <button class="btn btn-primary" id="refresh-btn">
                            🔄 Обновить
                        </button>
                        <button class="btn btn-secondary" id="export-btn">
                            📊 Экспорт
                        </button>
                        <button class="btn btn-secondary" id="clear-cache-btn">
                            🧹 Очистить кеш
                        </button>
                        <button class="btn btn-danger" id="disconnect-btn">
                            🔌 Отключиться
                        </button>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>Business Logger Bot v2.0</p>
            </div>
        </div>
    </div>

    <script>
        // Инициализация Telegram Web App
        const tg = window.Telegram.WebApp;
        let userData = null;
        let botStats = null;

        // Инициализация
        function init() {
            tg.ready();
            tg.expand();
            
            // Устанавливаем цвет темы
            tg.setHeaderColor('#667eea');
            tg.setBackgroundColor('#667eea');
            
            // Показываем кнопку закрытия
            tg.enableClosingConfirmation();
            
            // Загружаем данные
            loadUserData();
            
            // Устанавливаем обработчики
            setupEventListeners();
            
            // Скрываем загрузку и показываем контент
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('content').style.display = 'block';
            }, 1000);
        }

        // Загрузка данных пользователя
        function loadUserData() {
            // Получаем данные от Telegram Web App
            const webAppData = tg.initDataUnsafe;
            
            if (webAppData.user) {
                console.log('User data:', webAppData.user);
                // Отправляем запрос на получение данных пользователя
                sendMessage('get_user_data');
            }
            
            // Запрашиваем статистику
            sendMessage('get_stats');
        }

        // Отправка сообщения боту
        function sendMessage(action, data = {}) {
            const message = {
                action: action,
                data: data,
                timestamp: Date.now()
            };
            
            // Отправляем данные через Telegram Web App
            tg.sendData(JSON.stringify(message));
        }

        // Обработка данных от бота
        function handleBotData(data) {
            try {
                const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
                
                switch (parsedData.type) {
                    case 'user_data':
                        userData = parsedData.data;
                        updateUserData();
                        break;
                    case 'stats':
                        botStats = parsedData.data;
                        updateStats();
                        break;
                    case 'connection_status':
                        updateConnectionStatus(parsedData.data);
                        break;
                }
            } catch (error) {
                console.error('Error parsing bot data:', error);
            }
        }

        // Обновление данных пользователя
        function updateUserData() {
            if (!userData) return;
            
            // Обновляем настройки
            const settings = userData.settings || {};
            Object.keys(settings).forEach(key => {
                const toggle = document.querySelector(`[data-setting="${key}"]`);
                if (toggle) {
                    if (settings[key]) {
                        toggle.classList.add('active');
                    } else {
                        toggle.classList.remove('active');
                    }
                }
            });
            
            // Обновляем статистику пользователя
            const stats = userData.stats || {};
            updateStatCards(stats);
        }

        // Обновление статистики
        function updateStats() {
            if (!botStats) return;
            
            // Обновляем общую статистику
            updateStatCards(botStats);
        }

        // Обновление карточек статистики
        function updateStatCards(stats) {
            document.getElementById('messages-count').textContent = 
                (stats.received || 0) + (stats.sent || 0);
            document.getElementById('view-once-count').textContent = 
                stats.view_once || 0;
            document.getElementById('deleted-count').textContent = 
                stats.deleted || 0;
            document.getElementById('edited-count').textContent = 
                stats.edited || 0;
        }

        // Обновление статуса подключения
        function updateConnectionStatus(status) {
            const statusDiv = document.getElementById('connection-status');
            
            if (status.connected) {
                statusDiv.innerHTML = `
                    <div class="message">
                        <div class="message-title">
                            <span class="status-indicator status-online"></span>
                            Подключено активно
                        </div>
                        <div class="message-text">
                            Бизнес подключение: ${status.active_connections || 0} активных
                        </div>
                    </div>
                `;
            } else {
                statusDiv.innerHTML = `
                    <div class="message">
                        <div class="message-title">
                            <span class="status-indicator status-offline"></span>
                            Нет активных подключений
                        </div>
                        <div class="message-text">
                            Подключите бота к бизнес аккаунту
                        </div>
                    </div>
                `;
            }
        }

        // Установка обработчиков событий
        function setupEventListeners() {
            // Переключатели
            document.querySelectorAll('.toggle-switch').forEach(toggle => {
                toggle.addEventListener('click', function() {
                    const setting = this.dataset.setting;
                    const isActive = this.classList.contains('active');
                    
                    // Переключаем состояние
                    if (isActive) {
                        this.classList.remove('active');
                    } else {
                        this.classList.add('active');
                    }
                    
                    // Отправляем изменение в бот
                    sendMessage('update_setting', {
                        setting: setting,
                        value: !isActive
                    });
                });
            });
            
            // Кнопки действий
            document.getElementById('refresh-btn').addEventListener('click', () => {
                sendMessage('refresh_data');
                loadUserData();
            });
            
            document.getElementById('export-btn').addEventListener('click', () => {
                sendMessage('export_data');
            });
            
            document.getElementById('clear-cache-btn').addEventListener('click', () => {
                if (confirm('Вы уверены, что хотите очистить кеш?')) {
                    sendMessage('clear_cache');
                }
            });
            
            document.getElementById('disconnect-btn').addEventListener('click', () => {
                if (confirm('Вы уверены, что хотите отключиться?')) {
                    sendMessage('disconnect');
                    tg.close();
                }
            });
        }

        // Обработка сообщений от бота (если бот отправляет данные обратно)
        window.addEventListener('message', function(event) {
            if (event.data && event.data.type === 'telegram_bot_data') {
                handleBotData(event.data);
            }
        });

        // Инициализация при загрузке
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    </script>
</body>
</html>
