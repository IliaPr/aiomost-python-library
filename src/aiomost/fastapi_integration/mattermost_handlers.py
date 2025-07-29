"""
FastAPI обработчики для Mattermost интеграции
"""
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from aiomost.mattermost_models.button_query.button_query_model import MattermostButtonQuery
from aiomost.mattermost_dispatcher.dispatcher import Dispatcher


logger = logging.getLogger(__name__)


class MattermostFastAPIRouter:
    """
    Класс для создания FastAPI роутеров с готовыми обработчиками Mattermost событий
    """
    
    def __init__(
        self, 
        dispatcher: Dispatcher, 
        prefix: str = "/mattermost",
        tags: Optional[list] = None
    ):
        """
        Инициализация роутера
        
        Args:
            dispatcher: Диспетчер для обработки событий
            prefix: Префикс для всех роутов
            tags: Теги для OpenAPI документации
        """
        self.dispatcher = dispatcher
        self.router = APIRouter(prefix=prefix, tags=tags or ["mattermost"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Настройка всех роутов"""
        self._setup_button_action_handler()
        self._setup_webhook_handler()
        self._setup_slash_command_handler()
    
    def _setup_button_action_handler(self):
        """Настройка обработчика нажатий на кнопки"""
        
        @self.router.post("/action")
        async def handle_button_action(request: Request):
            """
            Обработчик нажатий на интерактивные кнопки Mattermost
            
            Принимает POST запросы от Mattermost при нажатии на кнопки
            и передает их в диспетчер для обработки.
            """
            try:
                logger.info("Button action received")
                data = await request.json()
                
                # Валидация данных
                if not data:
                    logger.warning("Empty button action data received")
                    raise HTTPException(status_code=400, detail="Empty data")
                
                # Преобразуем в объект с атрибутами
                event = MattermostButtonQuery(data)
                
                logger.debug(f"Processing button action: {event.trigger_id}")
                
                # Обработка запроса и отправка ответа
                response = await self.dispatcher.dispatch("button_query", event)
                
                if response is not None:
                    logger.info("Button action processed successfully")
                    return response
                else:
                    logger.info("Button action processed, no response")
                    return JSONResponse(
                        content={
                            "event_type": "button_query", 
                            "status": "processed",
                            "trigger_id": getattr(event, 'trigger_id', None)
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Error processing button action: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error processing button action: {str(e)}"
                )
    
    def _setup_webhook_handler(self):
        """Настройка общего webhook обработчика"""
        
        @self.router.post("/webhook")
        async def handle_webhook(request: Request):
            """
            Общий обработчик вебхуков от Mattermost
            
            Может обрабатывать различные типы событий от Mattermost
            """
            try:
                logger.info("Webhook received")
                data = await request.json()
                
                # Определяем тип события
                event_type = data.get("event", {}).get("event", "unknown")
                logger.info(f"Webhook event type: {event_type}")
                
                # Отправляем в диспетчер
                response = await self.dispatcher.dispatch("webhook", data)
                
                return response or {"status": "ok", "event_type": event_type}
                
            except Exception as e:
                logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error processing webhook: {str(e)}"
                )
    
    def _setup_slash_command_handler(self):
        """Настройка обработчика slash команд"""
        
        @self.router.post("/command")
        async def handle_slash_command(request: Request):
            """
            Обработчик slash команд от Mattermost
            
            Обрабатывает команды вида /command args
            """
            try:
                logger.info("Slash command received")
                
                # Для slash команд данные приходят как form data
                form_data = await request.form()
                data = dict(form_data)
                
                logger.info(f"Slash command: {data.get('command', 'unknown')}")
                
                # Отправляем в диспетчер
                response = await self.dispatcher.dispatch("slash_command", data)
                
                return response or {
                    "response_type": "ephemeral",
                    "text": "Command processed"
                }
                
            except Exception as e:
                logger.error(f"Error processing slash command: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error processing slash command: {str(e)}"
                )
    
    def get_router(self) -> APIRouter:
        """Возвращает настроенный FastAPI роутер"""
        return self.router


def create_mattermost_router(
    dispatcher: Dispatcher, 
    prefix: str = "/mattermost",
    tags: Optional[list] = None
) -> APIRouter:
    """
    Фабричная функция для создания Mattermost роутера
    
    Args:
        dispatcher: Диспетчер для обработки событий
        prefix: Префикс для роутов
        tags: Теги для документации
        
    Returns:
        Настроенный FastAPI роутер
        
    Example:
        ```python
        from aiomost.fastapi_integration import create_mattermost_router
        from aiomost.mattermost_dispatcher.dispatcher import Dispatcher
        
        dp = Dispatcher(state_manager=state_manager)
        mattermost_router = create_mattermost_router(dp)
        
        app.include_router(mattermost_router)
        ```
    """
    router_handler = MattermostFastAPIRouter(dispatcher, prefix, tags)
    return router_handler.get_router()
