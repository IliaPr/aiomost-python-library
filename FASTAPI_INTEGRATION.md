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

