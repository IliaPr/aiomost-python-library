from typing import Any, Dict, Optional
from aiomost.mattermost_models.base_model.base_model import BaseModel


class NotifyProps(BaseModel):
    """Настройки уведомлений пользователя."""
    email: Optional[str] = None
    push: Optional[str] = None
    desktop: Optional[str] = None
    desktop_sound: Optional[str] = None
    mention_keys: Optional[str] = None
    channel: Optional[str] = None
    first_name: Optional[str] = None


class Timezone(BaseModel):
    """Настройки часового пояса пользователя."""
    useAutomaticTimezone: Optional[bool] = None
    manualTimezone: Optional[str] = None
    automaticTimezone: Optional[str] = None


class User(BaseModel):
    """Класс для хранения данных о пользователе."""
    id: Optional[str] = None
    create_at: Optional[int] = None
    update_at: Optional[int] = None
    delete_at: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    auth_service: Optional[str] = None
    roles: Optional[str] = None
    locale: Optional[str] = None
    notify_props: Optional[NotifyProps] = None
    props: Optional[Dict[str, Any]] = None
    last_password_update: Optional[int] = None
    last_picture_update: Optional[int] = None
    failed_attempts: Optional[int] = None
    mfa_active: Optional[bool] = None
    timezone: Optional[Timezone] = None
    terms_of_service_id: Optional[str] = None
    terms_of_service_create_at: Optional[int] = None

    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"
