"""
Middleware для FastAPI интеграции с Mattermost.
"""

import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse


class MattermostMiddleware:
    """
    Middleware для обработки Mattermost запросов.
    """
    
    def __init__(self, app: Callable, logger: logging.Logger = None):
        self.app = app
        self.logger = logger or logging.getLogger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Логируем Mattermost запросы
            if request.url.path.startswith("/mattermost"):
                self.logger.info(f"Mattermost request: {request.method} {request.url.path}")
                
                # Добавляем заголовки для Mattermost
                response = await self.app(scope, receive, send)
                return response
        
        return await self.app(scope, receive, send)


def add_mattermost_headers(response: Response) -> Response:
    """
    Добавляет необходимые заголовки для Mattermost интеграции.
    
    Args:
        response: FastAPI Response объект
        
    Returns:
        Response с добавленными заголовками
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response


async def mattermost_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик ошибок для Mattermost интеграции.
    
    Args:
        request: FastAPI Request объект
        exc: Исключение
        
    Returns:
        JSONResponse с информацией об ошибке
    """
    logger = logging.getLogger(__name__)
    logger.error(f"Mattermost integration error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )
