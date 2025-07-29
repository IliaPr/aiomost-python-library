import json


class BaseModel:
    """Базовый класс для автоматического преобразования JSON в объект."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                # Рекурсивно превращаем словари в объекты
                setattr(self, key, BaseModel(**value))
            elif isinstance(value, list):
                setattr(self, key, [BaseModel(
                    **item) if isinstance(item, dict) else item for item in value])
            else:
                setattr(self, key, value)

    def to_json(self):
        """Конвертирует объект обратно в JSON."""
        return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False, separators=(',', ':'))
