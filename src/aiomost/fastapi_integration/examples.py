"""
Примеры использования AioMost с FastAPI
"""

from fastapi import FastAPI
from aiomost import (
    Dispatcher, 
    RedisStateManager,
    create_mattermost_router,
    MattermostLoggingMiddleware,
    MattermostSecurityMiddleware
)

# Пример 1: Базовая интеграция
def create_basic_app():
    """
    Создает базовое FastAPI приложение с Mattermost интеграцией
    """
    app = FastAPI(title="Mattermost Bot API")
    
    # Настройка состояния
    redis_url = "redis://localhost:6379/0"
    state_manager = RedisStateManager.from_url(redis_url)
    
    # Создание диспетчера
    dp = Dispatcher(state_manager=state_manager)
    
    # Создание и подключение Mattermost роутера
    mattermost_router = create_mattermost_router(dp)
    app.include_router(mattermost_router)
    
    return app, dp


# Пример 2: С middleware и безопасностью
def create_secure_app():
    """
    Создает FastAPI приложение с middleware и безопасностью
    """
    app = FastAPI(title="Secure Mattermost Bot API")
    
    # Добавляем middleware
    app.add_middleware(MattermostLoggingMiddleware)
    app.add_middleware(
        MattermostSecurityMiddleware,
        allowed_ips=["192.168.1.100", "10.0.0.1"],  # IP Mattermost сервера
        verify_token="your-webhook-token"
    )
    
    # Настройка диспетчера
    redis_url = "redis://localhost:6379/0"
    state_manager = RedisStateManager.from_url(redis_url)
    dp = Dispatcher(state_manager=state_manager)
    
    # Подключение роутера с кастомными настройками
    mattermost_router = create_mattermost_router(
        dp, 
        prefix="/api/v1/mattermost",
        tags=["mattermost-integration"]
    )
    app.include_router(mattermost_router)
    
    return app, dp


# Пример 3: Полная интеграция с обработчиками
def create_full_app():
    """
    Создает полное приложение с обработчиками событий
    """
    from aiomost import Router, MattermostBot
    
    app = FastAPI(title="Full Mattermost Integration")
    
    # Middleware
    app.add_middleware(MattermostLoggingMiddleware)
    
    # Настройка состояния и диспетчера
    redis_url = "redis://localhost:6379/0"
    state_manager = RedisStateManager.from_url(redis_url)
    dp = Dispatcher(state_manager=state_manager)
    
    # Создание бота
    bot = MattermostBot(
        url="https://your-mattermost.com",
        token="your-bot-token"
    )
    
    # Создание роутера для обработки событий
    main_router = Router()
    
    @main_router.button_query_handler()
    async def handle_button_press(query):
        """Обработчик нажатий на кнопки"""
        await bot.send_message(
            query.channel_id,
            f"Кнопка нажата: {query.context.get('action', 'unknown')}"
        )
    
    @main_router.message_handler()
    async def handle_message(message):
        """Обработчик сообщений"""
        if message.text.startswith("/hello"):
            await bot.send_message(
                message.channel_id,
                "Привет! 👋"
            )
    
    # Подключение роутеров
    dp.include_router(main_router)
    
    # FastAPI роутер
    mattermost_router = create_mattermost_router(dp)
    app.include_router(mattermost_router)
    
    return app, dp, bot


if __name__ == "__main__":
    import uvicorn
    
    # Запуск базового приложения
    app, dp = create_basic_app()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
