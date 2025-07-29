class Dispatcher:
    def __init__(self, state_manager=None):
        self.routers = []
        self.state_manager = state_manager

    def include_router(self, router):
        """
        Регистрирует новый роутер в диспетчере.
        Если в диспетчере есть state_manager, можно его назначить роутеру.
        """
        self.routers.append(router)
        router._parent_router = self
        # Если роутер ещё не имеет state_manager, можно установить его от диспетчера
        if self.state_manager and not router.state_manager:
            router.state_manager = self.state_manager

    async def dispatch(self, update_type: str, event, **kwargs):
        """
        Распространяет событие по всем роутерам,
        передавая state_manager, если он задан.
        """
        if self.state_manager:
            kwargs.setdefault("state_manager", self.state_manager)
        for router in self.routers:
            response = await router.propagate_event(update_type, event, **kwargs)
            if response is not None:
                return response
        return None
