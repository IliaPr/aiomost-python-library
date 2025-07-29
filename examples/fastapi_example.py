"""
Пример использования AioMost с FastAPI.
"""

from fastapi import FastAPI
from aiomost import (
    setup_mattermost_integration,
    Router,
    MattermostButtonQuery
)
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Mattermost Bot Example")

# Настраиваем Mattermost интеграцию
dp = setup_mattermost_integration(
    app, 
    redis_url="redis://localhost:6379/0"
)

# Создаем роутер для обработчиков
router = Router()

@router.button_query_handler()
async def handle_buttons(event: MattermostButtonQuery):
    """Обработчик нажатий на кнопки"""
    action = event.context.get("action", "unknown")
    
    if action == "hello":
        return {
            "update": {
                "message": "👋 Привет! Кнопка нажата!",
                "props": {}
            }
        }
    
    return {"text": f"Действие: {action}"}

# Добавляем роутер
dp.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
