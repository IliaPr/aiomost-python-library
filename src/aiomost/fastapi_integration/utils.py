"""
Утилиты для FastAPI интеграции.
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI

from ..mattermost_dispatcher.dispatcher import Dispatcher
from ..mattermost_state_storage.redis_state_manager import RedisStateManager
from .handlers import create_mattermost_router


class MattermostApp:
    """
    Класс для быстрой настройки FastAPI приложения с Mattermost интеграцией.
    """

    def __init__(
        self,
        app: FastAPI,
        redis_url: str,
        mattermost_prefix: str = "/mattermost"
    ):
        """
        Инициализация Mattermost приложения.

        Args:
            app: FastAPI приложение
            redis_url: URL для подключения к Redis
            mattermost_prefix: Префикс для Mattermost роутов
        """
        self.app = app
        self.redis_url = redis_url
        self.mattermost_prefix = mattermost_prefix

        # Инициализируем компоненты
        self.state_manager = RedisStateManager.from_url(redis_url)
        self.dispatcher = Dispatcher(state_manager=self.state_manager)

        # Создаем и подключаем роутер
        self.router = create_mattermost_router(
            self.dispatcher,
            prefix=mattermost_prefix
        )
        self.app.include_router(self.router)

    def include_router(self, router):
        """
        Добавляет роутер в диспетчер.

        Args:
            router: Роутер для добавления
        """
        self.dispatcher.include_router(router)

    def get_dispatcher(self) -> Dispatcher:
        """Возвращает диспетчер."""
        return self.dispatcher

    def get_state_manager(self) -> RedisStateManager:
        """Возвращает менеджер состояний."""
        return self.state_manager


def setup_mattermost_integration(
    app: FastAPI,
    redis_url: str,
    prefix: str = "/mattermost",
    routers: Optional[list] = None
) -> Dispatcher:
    """
    Быстрая настройка Mattermost интеграции для FastAPI приложения.

    Args:
        app: FastAPI приложение
        redis_url: URL для подключения к Redis
        prefix: Префикс для Mattermost роутов
        routers: Список роутеров для добавления

    Returns:
        Настроенный диспетчер

    Example:
        ```python
        from fastapi import FastAPI
        from aiomost.fastapi_integration import setup_mattermost_integration

        app = FastAPI()
        dp = setup_mattermost_integration(
            app, 
            "redis://localhost:6379/0"
        )

        # Добавляем свои роутеры (пример)
        # from your_handlers import your_router
        # dp.include_router(your_router)
        ```
    """
    # Создаем менеджер состояний
    state_manager = RedisStateManager.from_url(redis_url)

    # Создаем диспетчер
    dispatcher = Dispatcher(state_manager=state_manager)

    # Добавляем роутеры если есть
    if routers:
        for router in routers:
            dispatcher.include_router(router)

    # Создаем и подключаем FastAPI роутер
    mattermost_router = create_mattermost_router(dispatcher, prefix=prefix)
    app.include_router(mattermost_router)

    return dispatcher
