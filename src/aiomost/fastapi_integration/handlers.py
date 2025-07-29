"""
Готовые обработчики для FastAPI интеграции с Mattermost.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Request, HTTPException

try:
    from fastapi import APIRouter, Request
except ImportError:
    raise ImportError(
        "FastAPI не установлен. Установите его с помощью: pip install fastapi"
    )

from ..mattermost_models.button_query.button_query_model import MattermostButtonQuery
from ..mattermost_dispatcher.dispatcher import Dispatcher


class MattermostButtonHandler:
    """
    Класс для обработки нажатий на кнопки Mattermost в FastAPI приложениях.
    """
    
    def __init__(self, dispatcher: Dispatcher, logger: Optional[logging.Logger] = None):
        """
        Инициализация обработчика.
        
        Args:
            dispatcher: Диспетчер для обработки событий
            logger: Логгер для записи событий (опционально)
        """
        self.dispatcher = dispatcher
        self.logger = logger or logging.getLogger(__name__)
    
    async def handle_button_action(self, request: Request) -> Dict[str, Any]:
        """
        Обработчик нажатий на кнопки Mattermost.
        
        Args:
            request: FastAPI Request объект
            
        Returns:
            Dict с результатом обработки
            
        Raises:
            HTTPException: В случае ошибки обработки
        """
        try:
            self.logger.info("Button action received")
            data = await request.json()
            
            # Преобразуем в объект с атрибутами
            event = MattermostButtonQuery(data)
            
            # Обработка запроса и отправка ответа
            response = await self.dispatcher.dispatch("button_query", event)
            
            return response if response is not None else {
                "event_type": "button_query", 
                "data": data
            }
            
        except Exception as e:
            self.logger.error(f"Error handling button action: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def handle_webhook(self, request: Request) -> Dict[str, Any]:
        """
        Обработчик вебхуков Mattermost.
        
        Args:
            request: FastAPI Request объект
            
        Returns:
            Dict с результатом обработки
        """
        try:
            self.logger.info("Webhook received")
            data = await request.json()
            
            # Определяем тип события и обрабатываем
            event_type = data.get("event", "unknown")
            
            response = await self.dispatcher.dispatch(event_type, data)
            
            return response if response is not None else {
                "status": "ok",
                "event_type": event_type
            }
            
        except Exception as e:
            self.logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))


def create_mattermost_router(
    dispatcher: Dispatcher,
    prefix: str = "/mattermost",
    logger: Optional[logging.Logger] = None
) -> APIRouter:
    """
    Создает готовый FastAPI роутер для Mattermost интеграции.
    
    Args:
        dispatcher: Диспетчер для обработки событий
        prefix: Префикс для роутера (по умолчанию "/mattermost")
        logger: Логгер для записи событий
        
    Returns:
        Настроенный APIRouter
        
    Example:
        ```python
        from aiomost.fastapi_integration import create_mattermost_router
        from aiomost.mattermost_dispatcher import Dispatcher
        
        dp = Dispatcher()
        router = create_mattermost_router(dp)
        app.include_router(router)
        ```
    """
    router = APIRouter(prefix=prefix, tags=["mattermost"])
    handler = MattermostButtonHandler(dispatcher, logger)
    
    @router.post("/action")
    async def handle_button_action(request: Request):
        """Обработчик нажатий на кнопки"""
        return await handler.handle_button_action(request)
    
    @router.post("/webhook")
    async def handle_webhook(request: Request):
        """Обработчик вебхуков"""
        return await handler.handle_webhook(request)
    
    @router.get("/health")
    async def health_check():
        """Проверка здоровья сервиса"""
        return {"status": "healthy", "service": "mattermost-integration"}
    
    return router


def create_simple_mattermost_router(
    dispatcher: Dispatcher,
    prefix: str = "/mattermost"
) -> APIRouter:
    """
    Создает упрощенный роутер только с обработчиком кнопок.
    
    Args:
        dispatcher: Диспетчер для обработки событий
        prefix: Префикс для роутера
        
    Returns:
        Упрощенный APIRouter
    """
    router = APIRouter(prefix=prefix)
    logger = logging.getLogger(__name__)
    
    @router.post("/action")
    async def handle_button_action(request: Request):
        """Обработчик нажатий на кнопки"""
        logger.info("Button action received")
        data = await request.json()
        
        # Преобразуем в объект с атрибутами
        event = MattermostButtonQuery(data)
        
        # Обработка запроса и отправка ответа
        response = await dispatcher.dispatch("button_query", event)
        return response if response is not None else {
            "event_type": "button_query", 
            "data": data
        }
    
    return router
