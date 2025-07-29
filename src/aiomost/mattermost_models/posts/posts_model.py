import json
from aiomost.mattermost_models.base_model.base_model import BaseModel


class PostProps:
    def __init__(self, disable_group_highlight=False, attachments=None, **kwargs):
        self.disable_group_highlight = disable_group_highlight
        self.attachments = attachments if attachments is not None else []

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, key, default=None):
        """Метод для доступа к атрибутам как к словарю"""
        return getattr(self, key, default)

    def __getitem__(self, key):
        """Позволяет использовать props['key'] синтаксис"""
        return getattr(self, key)

    def __contains__(self, key):
        """Позволяет использовать 'key' in props синтаксис"""
        return hasattr(self, key)

    def to_dict(self):
        """Преобразует объект в словарь для сериализации"""
        return {key: value for key, value in self.__dict__.items()}


class PostMetadata(BaseModel):
    def __init__(self, embeds=None, emojis=None, files=None, images=None, reactions=None, priority=None, acknowledgements=None):
        self.embeds = embeds or []
        self.emojis = emojis or []
        self.files = files or []
        self.images = images or {}
        self.reactions = reactions or []
        self.priority = priority or {}
        self.acknowledgements = acknowledgements or []


class Post(BaseModel):
    def __init__(self, id, create_at, update_at, edit_at, delete_at, is_pinned, user_id, channel_id, root_id, original_id,
                 message, type, props=None, hashtags='', file_ids=None, pending_post_id='', remote_id='',
                 reply_count=0, last_reply_at=0, participants=None, metadata=None):
        self.id = id
        self.create_at = create_at
        self.update_at = update_at
        self.edit_at = edit_at
        self.delete_at = delete_at
        self.is_pinned = is_pinned
        self.user_id = user_id
        self.channel_id = channel_id
        self.root_id = root_id
        self.original_id = original_id
        self.message = message
        self.type = type
        self.props = PostProps(**props) if isinstance(props, dict) else props
        self.hashtags = hashtags
        self.file_ids = file_ids or []
        self.pending_post_id = pending_post_id
        self.remote_id = remote_id
        self.reply_count = reply_count
        self.last_reply_at = last_reply_at
        self.participants = participants or []
        self.metadata = PostMetadata(
            **metadata) if isinstance(metadata, dict) else metadata

    @classmethod
    def parse_post(cls, post_data):
        return cls(**(json.loads(post_data) if isinstance(post_data, str) else post_data))


class MessageData(BaseModel):
    def __init__(self, channel_display_name, channel_name, channel_type, post, sender_name, set_online, team_id, mentions=None, image=None, otherFile=None, **kwargs):
        self.channel_display_name = channel_display_name
        self.channel_name = channel_name
        self.channel_type = channel_type
        self.sender_name = sender_name
        self.set_online = set_online
        self.team_id = team_id

        self.image = image
        self.otherFile = otherFile

        if isinstance(mentions, str):
            self.mentions = json.loads(mentions)
        else:
            self.mentions = mentions or []

        if isinstance(post, str):
            self.post = Post(**json.loads(post))
        else:
            self.post = post

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def parse_post_data(cls, data):
        try:
            if isinstance(data.get("post"), str):
                data["post"] = json.loads(data["post"])
            return cls(**data)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            import logging
            logging.error(
                f"Ошибка при парсинге MessageData: {e}, данные: {data}")
            return cls(
                channel_display_name=data.get('channel_display_name', ''),
                channel_name=data.get('channel_name', ''),
                channel_type=data.get('channel_type', ''),
                post=data.get('post', {}),
                sender_name=data.get('sender_name', ''),
                set_online=data.get('set_online', False),
                team_id=data.get('team_id', ''),
                **{k: v for k, v in data.items() if k not in [
                    'channel_display_name', 'channel_name', 'channel_type',
                    'post', 'sender_name', 'set_online', 'team_id'
                ]}
            )


class MessageBroadcast(BaseModel):
    def __init__(self, omit_users=None, user_id='', channel_id='', team_id='', connection_id='', omit_connection_id='', **kwargs):
        self.omit_users = omit_users or {}
        self.user_id = user_id
        self.channel_id = channel_id
        self.team_id = team_id
        self.connection_id = connection_id
        self.omit_connection_id = omit_connection_id

        for key, value in kwargs.items():
            setattr(self, key, value)


class MessageEvent(BaseModel):
    def __init__(self, event, data, broadcast, seq):
        self.event = event  # <-- вот оно, это и есть тип события
        self.data = MessageData(**data) if isinstance(data, dict) else data
        self.broadcast = MessageBroadcast(
            **broadcast) if isinstance(broadcast, dict) else broadcast
        self.seq = seq

    @property
    def event_type(self):
        return self.event

    @classmethod
    def parse_message_event(cls, values):
        try:
            if isinstance(values.get("data"), str):
                values["data"] = json.loads(values["data"])
            return cls(**values)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            import logging
            logging.error(
                f"Ошибка при парсинге MessageEvent: {e}, данные: {values}")
            return cls(
                event=values.get('event', ''),
                data=values.get('data', {}),
                broadcast=values.get('broadcast', {}),
                seq=values.get('seq', 0)
            )
