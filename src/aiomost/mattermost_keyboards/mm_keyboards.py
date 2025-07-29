import logging
from typing import List, Dict

# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_actions(base_url: str, buttons: List[tuple]) -> List[Dict]:
    """
    Генерирует JSON с кнопками для интеграции Mattermost.

    :param base_url: Базовый URL для интеграции.
    :param buttons: Список кнопок, где каждая - это (id, name, action).
    :return: JSON-объект со списком кнопок.
    """
    actions = [
        {
            "id": button_id,
            "name": button_name,
            "integration": {
                "url": f"{base_url}/mattermost/action/",
                "context": {
                    "action": action
                }
            }
        }
        for button_id, button_name, action in buttons
    ]

    logger.debug(f"Generated actions: {actions}")

    return actions
