import asyncio
import json
import logging
import ssl
import websockets

from aiomost.mattermost_models.posts.posts_model import MessageEvent
from aiomost.mattermost_models.user.user_added.user_added_models import UserAddedEvent


logging.getLogger('websockets').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class MattermostUpdate:
    def __init__(self, event_type: str, data: dict):
        self.event_type = event_type
        self.data = data

    def __str__(self):
        return f"Event: {self.event_type}, Data: {self.data}"

    def to_json(self):
        cleaned_data = self._clean_json(self.data)
        return json.dumps({
            "event_type": self.event_type,
            "data": cleaned_data
        }, ensure_ascii=False, separators=(',', ':'))

    def _clean_json(self, data):
        if isinstance(data, dict):
            return {key: self._clean_json(value) for key, value in data.items()}
        elif isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        elif isinstance(data, list):
            return [self._clean_json(item) for item in data]
        return data


async def mattermost_ws_listener(routers, ws_url: str, token: str):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    reconnect_delay = 1

    while True:
        try:
            async with websockets.connect(ws_url, ssl=ssl_context) as ws:
                auth_data = {
                    "seq": 1,
                    "action": "authentication_challenge",
                    "data": {"token": token}
                }
                await ws.send(json.dumps(auth_data))
                logger.info("✅ Подключение к WebSocket установлено!")

                reconnect_delay = 1  # Сброс задержки при успешном подключении

                while True:
                    try:
                        message = await ws.recv()
                        data = json.loads(message)
                        print(data)

                        event_type = data.get("event")
                        if event_type == "user_added":
                            try:
                                # Универсальный парсер
                                event = UserAddedEvent(**data)
                                for router in routers:
                                    await router.propagate_event(event_type, event)
                            except Exception as e:
                                logger.error(
                                    f"❌ Ошибка обработки события 'user_added': {e}")
                                logger.debug(f"Данные события: {data}")

                        elif event_type == "posted":
                            try:
                                event = MessageEvent(**data)

                                # Игнорируем сообщения от ботов
                                if (hasattr(event.data.post, 'props') and
                                    event.data.post.props and
                                        event.data.post.props.get("from_bot") == "true"):
                                    logger.debug(
                                        f"🤖 Игнорируем сообщение от бота: {event.data.post.id}")
                                    continue

                                # Игнорируем системные сообщения
                                if hasattr(event.data.post, 'type') and event.data.post.type:
                                    logger.debug(
                                        f"📋 Игнорируем системное сообщение типа '{event.data.post.type}': {event.data.post.id}")
                                    continue

                                for router in routers:
                                    await router.propagate_event(event_type, event)
                            except Exception as e:
                                logger.error(
                                    f"❌ Ошибка обработки события 'posted': {e}")
                                logger.debug(f"Данные события: {data}")

                        else:
                            try:
                                update = MattermostUpdate(event_type, data)
                                for router in routers:
                                    await router.propagate_event(event_type, update)
                            except Exception as e:
                                logger.error(
                                    f"❌ Ошибка обработки события '{event_type}': {e}")
                                logger.debug(f"Данные события: {data}")

                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Ошибка парсинга JSON сообщения: {e}")
                        logger.debug(f"Проблемное сообщение: {message}")
                    except websockets.ConnectionClosed:
                        # Переподключение будет обработано во внешнем блоке
                        raise
                    except Exception as e:
                        logger.error(
                            f"❌ Неожиданная ошибка при обработке сообщения: {e}")
                        logger.debug(
                            f"Сообщение: {message if 'message' in locals() else 'Не удалось получить'}")
                        # Продолжаем работу, не прерывая соединение
        except websockets.ConnectionClosed as e:
            logger.warning(f"⚠️ WebSocket соединение закрыто")
            logger.debug(f"Детали закрытия соединения: {e}")
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")
        except websockets.InvalidURI as e:
            logger.error(f"❌ Неверный URI WebSocket: {e}")
            logger.error(f"Проверьте URL: {ws_url}")
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")
        except websockets.InvalidHandshake as e:
            logger.error(f"❌ Ошибка рукопожатия WebSocket: {e}")
            logger.error(
                "Возможно, проблема с токеном авторизации или сервером")
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")
        except ssl.SSLError as e:
            logger.error(f"❌ Ошибка SSL: {e}")
            logger.error("Проблема с SSL-сертификатом или шифрованием")
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")
        except ConnectionRefusedError as e:
            logger.error(f"❌ Соединение отклонено: {e}")
            logger.error(
                f"Сервер {ws_url} недоступен или отклоняет подключения")
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")
        except asyncio.TimeoutError as e:
            logger.error(f"❌ Таймаут соединения: {e}")
            logger.error("Сервер не отвечает в течение допустимого времени")
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")
        except Exception as e:
            logger.error(
                f"❌ Неожиданная ошибка WebSocket: {type(e).__name__}: {e}")
            logger.debug(f"Полная информация об ошибке:", exc_info=True)
            logger.info(f"🔄 Переподключение через {reconnect_delay} секунд...")

        await asyncio.sleep(reconnect_delay)
        # Экспоненциальная задержка
        reconnect_delay = min(reconnect_delay * 2, 60)
