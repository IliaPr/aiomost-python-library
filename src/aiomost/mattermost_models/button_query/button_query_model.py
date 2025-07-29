import json


class DotDict(dict):
    """Удобный класс для доступа к ключам через точку"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MattermostButtonQuery:
    def __init__(self, data: dict):
        self.event_type = "button_query"
        self.data = DotDict(data)

        # Извлекаем 'context' и другие поля с обработкой отсутствующих значений
        # post_id может быть в корне
        self.post_id = self.data.get("post_id", None)
        self.action = self.data.context.get(
            "action", None) if "context" in self.data else None  # action внутри context
        self.user_id = self.data.get("user_id", None)
        self.channel_id = self.data.get("channel_id", None)
        self.trigger_id = self.data.get("trigger_id", None)

        # Дополнительно обрабатываем другие ключи, если они существуют
        self.team_id = self.data.get("team_id", None)
        self.team_domain = self.data.get("team_domain", None)
        self.data_source = self.data.get("data_source", None)

    def __str__(self):
        # Для удобства вывода всех полей
        return (f"ButtonQuery: Action={self.action}, PostID={self.post_id}, "
                f"UserID={self.user_id}, ChannelID={self.channel_id}, "
                f"TriggerID={self.trigger_id}, TeamID={self.team_id}, "
                f"TeamDomain={self.team_domain}, DataSource={self.data_source}")

    def to_json(self):
        """Компактное преобразование в JSON с сохранением всех данных"""
        return json.dumps({
            "event_type": self.event_type,
            "action": self.action,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "trigger_id": self.trigger_id,
            "team_id": self.team_id,
            "team_domain": self.team_domain,
            "data_source": self.data_source
        }, ensure_ascii=False, separators=(',', ':'))
