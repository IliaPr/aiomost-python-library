# AioMost

Asynchronous Python library for Mattermost bot development with built-in FastAPI integration.

## 🚀 Features

- ✅ Asynchronous Mattermost API client
- ✅ WebSocket support for real-time events  
- ✅ **Built-in FastAPI integration** with ready-to-use handlers
- ✅ Modular architecture with routers, filters, and handlers
- ✅ State management for conversations
- ✅ Button and keyboard support
- ✅ Comprehensive Mattermost models
- ✅ Security middleware for webhook validation
- ✅ Logging middleware for debugging

## 📦 Installation

```bash
pip install aiomost
```

For development:
```bash
pip install -e ".[dev]"
```

## 🔥 Quick Start with FastAPI

### Basic Integration

```python
from fastapi import FastAPI
from aiomost import (
    Dispatcher, 
    RedisStateManager,
    create_mattermost_router
)

# Create FastAPI app
app = FastAPI()

# Setup state management
redis_url = "redis://localhost:6379/0"
state_manager = RedisStateManager.from_url(redis_url)

# Create dispatcher
dp = Dispatcher(state_manager=state_manager)

# Create and include Mattermost router
mattermost_router = create_mattermost_router(dp)
app.include_router(mattermost_router)

# Now your app has these endpoints:
# POST /mattermost/action   - Button clicks handler
# POST /mattermost/webhook  - General webhooks
# POST /mattermost/command  - Slash commands
```

### With Security and Logging

```python
from fastapi import FastAPI
from aiomost import (
    create_mattermost_router,
    MattermostLoggingMiddleware,
    MattermostSecurityMiddleware,
    Dispatcher,
    RedisStateManager
)

app = FastAPI()

# Add security middleware
app.add_middleware(
    MattermostSecurityMiddleware,
    allowed_ips=["192.168.1.100"],  # Your Mattermost server IP
    verify_token="your-webhook-secret"
)

# Add logging middleware
app.add_middleware(MattermostLoggingMiddleware)

# Setup dispatcher and router
state_manager = RedisStateManager.from_url("redis://localhost:6379/0")
dp = Dispatcher(state_manager=state_manager)
mattermost_router = create_mattermost_router(dp, prefix="/api/v1/mattermost")

app.include_router(mattermost_router)
```

## 🎯 Event Handlers

### Button Click Handler

```python
from aiomost import Router, MattermostBot

# Create router
router = Router()
bot = MattermostBot("https://mattermost.com", "bot-token")

@router.button_query_handler()
async def handle_button_click(query):
    """Handles button clicks from interactive messages"""
    action = query.context.get("action")
    
    if action == "approve":
        await bot.send_message(
            query.channel_id,
            "✅ Approved!"
        )
    elif action == "reject":
        await bot.send_message(
            query.channel_id, 
            "❌ Rejected!"
        )

# Include router in dispatcher
dp.include_router(router)
```

### Message Handler

```python
@router.message_handler()
async def handle_message(message):
    """Handles incoming messages"""
    if message.text.startswith("/hello"):
        keyboard = InlineKeyboard()
        keyboard.add_button("Say Hi 👋", callback_data="hi")
        keyboard.add_button("Say Bye 👋", callback_data="bye")
        
        await bot.send_message(
            message.channel_id,
            "Choose an action:",
            keyboard=keyboard
        )
```

## 🏗️ Migration from Manual Implementation

### Before (Manual FastAPI handler):

```python
@app.post("/mattermost/action")
async def handle_button_action(request: Request):
    logger.info("Button action received")
    data = await request.json()
    event = MattermostButtonQuery(data)
    response = await dp.dispatch("button_query", event)
    return response if response is not None else {"event_type": "button_query", "data": data}
```

### After (Using AioMost):

```python
from aiomost import create_mattermost_router

# Just one line!
mattermost_router = create_mattermost_router(dp)
app.include_router(mattermost_router)

# Includes all handlers:
# - Button actions (/mattermost/action)
# - Webhooks (/mattermost/webhook) 
# - Slash commands (/mattermost/command)
# - Error handling
# - Logging
# - Response formatting
```

## 🛠️ Advanced Usage

### Custom Router Configuration

```python
from aiomost.fastapi_integration import MattermostFastAPIRouter

# Create custom router
mattermost_handler = MattermostFastAPIRouter(
    dispatcher=dp,
    prefix="/custom/mattermost",
    tags=["custom-integration"]
)

# Get the router
router = mattermost_handler.get_router()
app.include_router(router)
```

### State Management

```python
from aiomost import Router

@router.button_query_handler()
async def stateful_handler(query, state):
    """Handler with state management"""
    # Get current state
    current_state = await state.get_state(query.user_id)
    
    if current_state == "waiting_for_confirmation":
        await bot.send_message(query.channel_id, "Confirmed!")
        await state.clear_state(query.user_id)
    else:
        await state.set_state(query.user_id, "waiting_for_confirmation")
        await bot.send_message(query.channel_id, "Please confirm your action")
```

## 📚 API Reference

### Core Classes

- **`MattermostBot`**: Main bot client for API operations
- **`Router`**: Event routing and handling
- **`Dispatcher`**: Event dispatching system
- **`RedisStateManager`**: Redis-based state storage

### FastAPI Integration

- **`create_mattermost_router(dispatcher, prefix="/mattermost")`**: Factory function
- **`MattermostFastAPIRouter`**: Full-featured router class
- **`MattermostLoggingMiddleware`**: Request/response logging
- **`MattermostSecurityMiddleware`**: IP and token validation

### Models

- **`MattermostButtonQuery`**: Button click events
- **`BaseModel`**: Base model for all Mattermost objects

## 📋 Requirements

- Python 3.8+
- FastAPI 0.68.0+
- Redis (for state management)
- Mattermost server

## 🔧 Development

```bash
git clone https://github.com/yourusername/aiomost.git
cd aiomost
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

## 📖 Examples

Check out the `examples.py` file for complete working examples:

- Basic FastAPI integration
- Secure setup with middleware
- Full bot with event handlers

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License
