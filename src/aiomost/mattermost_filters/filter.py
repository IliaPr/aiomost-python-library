from typing import Any, Protocol


class BaseFilter(Protocol):
    async def __call__(self, event: Any) -> bool:
        raise NotImplementedError
