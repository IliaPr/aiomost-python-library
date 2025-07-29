import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Union

from aiomost.mattermost_state_storage.matter_states import State
from aiomost.mattermost_state_storage.redis_state_manager import RedisStateManager


def inject_state(param_name: str = "state"):
    """
    Декоратор, который добавляет state_manager в параметры обработчика, если он ожидается.
    """
    def decorator(handler: Callable):
        async def wrapper(event, **kwargs):
            state_manager = kwargs.get("state_manager")
            sig = inspect.signature(handler)

            if param_name in sig.parameters and state_manager:
                kwargs[param_name] = state_manager

            return await handler(event, **kwargs)

        return wrapper
    return decorator


class Router:
    """
    Роутер для обработки событий Mattermost с поддержкой управления состоянием.
    """

    def __init__(self, name: Optional[str] = None, bot_user_id: Optional[str] = None, state_manager: Optional[RedisStateManager] = None) -> None:
        """
        Args:
            name: Имя роутера (опционально).
            bot_user_id: ID бота в Mattermost.
            state_manager: Экземпляр RedisStateManager для управления состоянием.
        """
        self.name = name or hex(id(self))
        self.sub_routers: List["Router"] = []
        self.bot_user_id = bot_user_id or "sxh6197ftffy5bcr54afro6bwr"
        self.state_manager = state_manager

        # Создаем наблюдатели событий
        self.message = EventObserver("message", self)
        self.errors = EventObserver("error", self)
        self.posted = EventObserver("posted", self)
        self.user_added = EventObserver("user_added", self)
        self.button_query = EventObserver("button_query", self)

        self.observers: Dict[str, EventObserver] = {
            "message": self.message,
            "error": self.errors,
            "posted": self.posted,
            "user_added": self.user_added,
            "button_query": self.button_query,
        }

    async def propagate_event(self, update_type: str, event, **kwargs: Any) -> Any:
        """
        Распространяет событие, передавая state_manager в обработчики.
        """
        if update_type == "posted":
            user_id = event.data.post.user_id
            if user_id == self.bot_user_id:
                return None

        observer = self.observers.get(update_type)
        if observer:
            if "state_manager" not in kwargs:
                kwargs["state_manager"] = self.state_manager
            response = await observer.trigger(event, **kwargs)
            if response is not None:
                return response

        # Передаем событие в дочерние роутеры
        for router in self.sub_routers:
            if "state_manager" not in kwargs:
                kwargs["state_manager"] = self.state_manager
            response = await router.propagate_event(update_type, event, **kwargs)
            if response is not None:
                return response
        return None


class EventObserver:
    """
    Наблюдатель событий для роутера с поддержкой фильтров, состояний и кнопок.
    """

    def __init__(self, event_name: str, router: Router) -> None:
        self.event_name = event_name
        self.router = router
        self.handlers: List[Dict[str, Any]] = []

    def register(self, handler: Callable, filters: List[Callable], required_state: Optional[State] = None) -> None:
        """
        Регистрирует обработчик события с фильтрами и required_state.
        """
        self.handlers.append({
            'handler': handler,
            'filters': filters,
            'required_state': required_state,
        })

    def __call__(
        self, *filters: Callable, button_data: Optional[Union[str, Callable[[str], bool]]] = None, required_state: Optional[State] = None
    ) -> Callable:
        """
        Декоратор для регистрации обработчиков событий.
        Поддерживает:
        - Фильтры (`filters`).
        - Проверку состояния (`required_state`).
        - Фильтрацию по кнопкам (`button_data`), в том числе `startswith()`.
        """
        def decorator(handler: Callable) -> Callable:
            handler = inject_state()(handler)
            filters_list = list(filters)

            if button_data:
                async def button_filter(event):
                    # Логируем структуру event и context

                    context = event.data.get("context", {})
                    action = context.get("action", None)

                    if not action:
                        return False

                    if isinstance(button_data, str):
                        return action == button_data
                    elif callable(button_data):
                        return button_data(action)
                    return False

                filters_list.insert(0, button_filter)

            async def wrapper(event, **kwargs):
                for filter_func in filters_list:
                    if not await filter_func(event):
                        return None

                state_manager = kwargs.get('state_manager')
                if required_state and state_manager:
                    user_id = state_manager.get_user_id_from_event(event)
                    if user_id:
                        current_state_str = await state_manager.get_state(user_id)
                        if current_state_str != required_state.state:
                            return None

                return await handler(event, **kwargs)

            self.register(wrapper, filters_list, required_state)
            return wrapper

        return decorator

    async def trigger(self, event, **kwargs):
        """
        Вызывает все зарегистрированные обработчики для события.
        При обработке состояний следует логике aiogram - после установки состояния 
        прерывает выполнение текущего обработчика.
        """
        # Множество флагов для отслеживания, были ли обработаны фильтры
        handler_executed = False
        state_manager = kwargs.get('state_manager')
        
        # Если это событие posted или button_query, получаем user_id и текущее состояние
        user_id = None
        current_state_str = None
        
        if state_manager and hasattr(event, 'event_type'):
            if event.event_type in ["posted", "button_query"]:
                user_id = state_manager.get_user_id_from_event(event)
                if user_id:
                    current_state_str = await state_manager.get_state(user_id)
        
        # Сначала обрабатываем обработчики с состояниями, если текущее состояние задано
        if current_state_str:
            for handler_data in self.handlers:
                handler = handler_data['handler']
                filters = handler_data['filters']
                required_state = handler_data['required_state']
                
                # Если у обработчика нет требуемого состояния или оно не совпадает с текущим - пропускаем
                if not required_state or required_state.state != current_state_str:
                    continue
                
                # Проверяем фильтры
                filters_passed = True
                for filter_func in filters:
                    if not await filter_func(event):
                        filters_passed = False
                        break
                
                if not filters_passed:
                    continue
                
                # Если дошли до этой точки - и состояние совпадает, и фильтры прошли
                # Вызываем обработчик и помечаем, что был выполнен обработчик с состоянием
                await handler(event, **kwargs)
                handler_executed = True
                # В стиле aiogram прерываем обработку после первого совпадения по состоянию
                return None
        
        # Если обработчик состояния не был вызван, пробуем обычные обработчики
        if not handler_executed:
            for handler_data in self.handlers:
                handler = handler_data['handler']
                filters = handler_data['filters']
                required_state = handler_data['required_state']
                
                # Пропускаем обработчики, требующие состояния
                if required_state:
                    continue
                
                # Проверяем фильтры
                filters_passed = True
                for filter_func in filters:
                    if not await filter_func(event):
                        filters_passed = False
                        break
                
                if not filters_passed:
                    continue
                
                # Вызываем обработчик
                result = await handler(event, **kwargs)
                handler_executed = True
                
                # Проверяем, было ли установлено новое состояние в результате выполнения обработчика
                if state_manager and user_id:
                    new_state = await state_manager.get_state(user_id)
                    if new_state and new_state != current_state_str:
                        # Если состояние изменилось, прерываем выполнение остальных обработчиков
                        # Это поведение как в aiogram - после установки состояния ожидаем следующее событие
                        return result
        
        return None
