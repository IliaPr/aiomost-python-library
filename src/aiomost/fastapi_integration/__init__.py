"""
FastAPI интеграция для AioMost.
Готовые обработчики и утилиты для интеграции с FastAPI.
"""

from .handlers import MattermostButtonHandler, create_mattermost_router
from .middleware import MattermostMiddleware
from .utils import setup_mattermost_integration, MattermostApp

__all__ = [
    'MattermostButtonHandler',
    'create_mattermost_router',
    'MattermostMiddleware',
    'setup_mattermost_integration',
    'MattermostApp'
]
