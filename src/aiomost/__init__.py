"""
AioMost - Asynchronous Python library for Mattermost bot development.
"""

__version__ = "0.1.0"

# Основные компоненты
from .mattermost_dispatcher.dispatcher import Dispatcher
from .mattermost_routers.mm_routers import Router
from .mattermost_state_storage.redis_state_manager import RedisStateManager
from .mattermost_actions.mm_actions import MMBot

# Модели
from .mattermost_models.button_query.button_query_model import MattermostButtonQuery
from .mattermost_models.posts.posts_model import *
from .mattermost_models.user.user_info.user_info_models import *

# Фильтры
from .mattermost_filters.filter import *

# Клавиатуры
from .mattermost_keyboards.mm_keyboards import *

# Состояния
from .mattermost_states.state import State

# FastAPI интеграция (опционально)
try:
    from .fastapi_integration import (
        MattermostButtonHandler,
        create_mattermost_router,
        setup_mattermost_integration,
        MattermostApp
    )
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


__all__ = [
    # Основные компоненты
    "Dispatcher",
    "Router", 
    "RedisStateManager",
    "MMBot",
    
    # Модели
    "MattermostButtonQuery",
    
    # Состояния
    "State",
]

# Добавляем FastAPI компоненты если доступны
if _HAS_FASTAPI:
    __all__.extend([
        "MattermostButtonHandler",
        "create_mattermost_router", 
        "setup_mattermost_integration",
        "MattermostApp"
    ])
