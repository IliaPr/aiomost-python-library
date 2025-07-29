# FastAPI Интеграция для AioMost

Этот модуль предоставляет готовые компоненты для интеграции AioMost с FastAPI приложениями.

## Установка

```bash
# Установка с FastAPI поддержкой
pip install aiomost[fastapi]

# Или отдельно
pip install aiomost fastapi uvicorn
```

## Быстрый старт

### Способ 1: Упрощенная настройка

```python
from fastapi import FastAPI
from aiomost import setup_mattermost_integration

app = FastAPI()

# Быстрая настройка Mattermost интеграции
dispatcher = setup_mattermost_integration(
    app, 
    redis_url="redis://localhost:6379/0"
)

# Добавляем свои роутеры
from my_handlers import my_router
dispatcher.include_router(my_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Способ 2: Ручная настройка

```python
from fastapi import FastAPI
from aiomost import Dispatcher, RedisStateManager, create_mattermost_router

app = FastAPI()

# Настраиваем компоненты
redis_url = "redis://localhost:6379/0"
state_manager = RedisStateManager.from_url(redis_url)
dispatcher = Dispatcher(state_manager=state_manager)

# Создаем роутер для Mattermost
mattermost_router = create_mattermost_router(dispatcher)
app.include_router(mattermost_router)

# Добавляем свои обработчики
from my_handlers import my_router
dispatcher.include_router(my_router)
```

### Способ 3: Класс MattermostApp

```python
from fastapi import FastAPI
from aiomost import MattermostApp

app = FastAPI()

# Создаем Mattermost приложение
mattermost_app = MattermostApp(
    app, 
    redis_url="redis://localhost:6379/0",
    mattermost_prefix="/mattermost"
)

# Добавляем роутеры
from my_handlers import my_router
mattermost_app.include_router(my_router)

# Получаем диспетчер для дополнительных настроек
dp = mattermost_app.get_dispatcher()
```

## Обработчики

### Готовые эндпоинты

После настройки автоматически создаются следующие эндпоинты:

- `POST /mattermost/action` - обработчик нажатий на кнопки
- `POST /mattermost/webhook` - обработчик вебхуков  
- `GET /mattermost/health` - проверка здоровья сервиса

### Использование в существующем проекте

Замените свой обработчик:

```python
# Было
@mattermost_router.post("/action")
async def handle_button_action(request: Request):
    logger.info("Button action received")
    data = await request.json()
    event = MattermostButtonQuery(data)
    response = await dp.dispatch("button_query", event)
    return response if response is not None else {"event_type": "button_query", "data": data}
```

```python
# Стало
from aiomost import create_mattermost_router

# Просто используйте готовый роутер
mattermost_router = create_mattermost_router(dp)
app.include_router(mattermost_router)
```

### Кастомизация обработчиков

```python
from aiomost import MattermostButtonHandler
import logging

# Создаем кастомный обработчик
logger = logging.getLogger("my_app")
handler = MattermostButtonHandler(dispatcher, logger)

# Используем в роутере
@app.post("/custom/action")
async def custom_action(request: Request):
    return await handler.handle_button_action(request)
```

## Примеры использования

### Полный пример приложения

```python
from fastapi import FastAPI
from aiomost import (
    setup_mattermost_integration, 
    Router, 
    MattermostButtonQuery
)
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="My Mattermost Bot")

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
    if event.context.action == "hello":
        return {
            "update": {
                "message": "Привет! Кнопка нажата!",
                "props": {}
            }
        }
    
    return {"text": "Неизвестное действие"}

# Добавляем роутер
dp.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Интеграция с существующим проектом

```python
# config.py
REDIS_URL = "redis://localhost:6379/0"

# main.py  
from fastapi import FastAPI
from aiomost import create_mattermost_router, Dispatcher, RedisStateManager

# Импортируем существующие роутеры
from handlers.main_router import main_router
from handlers.welcome_router import welcome_router

app = FastAPI()

# Настраиваем Mattermost
state_manager = RedisStateManager.from_url(REDIS_URL)
dp = Dispatcher(state_manager=state_manager)

# Добавляем существующие роутеры
dp.include_router(main_router)
dp.include_router(welcome_router)

# Создаем FastAPI роутер с готовыми обработчиками
mattermost_router = create_mattermost_router(dp, prefix="/mattermost")
app.include_router(mattermost_router)
```

## Миграция существующего кода

### Шаг 1: Установите обновленную библиотеку

```bash
pip install aiomost[fastapi]
```

### Шаг 2: Замените обработчики

```python
# Удалите старый код
# @mattermost_router.post("/action")
# async def handle_button_action(request: Request):
#     ...

# Добавьте новый
from aiomost import create_mattermost_router
mattermost_router = create_mattermost_router(dp)
app.include_router(mattermost_router)
```

### Шаг 3: Обновите импорты (если нужно)

```python
# Старые импорты остаются теми же
from aiomost.mattermost_dispatcher.dispatcher import Dispatcher
from aiomost.mattermost_state_storage.redis_state_manager import RedisStateManager

# Новые импорты
from aiomost import create_mattermost_router  # Новое!
```

## Преимущества

✅ **Готовые обработчики** - не нужно писать boilerplate код  
✅ **Обработка ошибок** - встроенная обработка исключений  
✅ **Логирование** - автоматическое логирование событий  
✅ **Типизация** - полная поддержка типов  
✅ **Гибкость** - можно кастомизировать под свои нужды  
✅ **Совместимость** - работает с существующим кодом  

