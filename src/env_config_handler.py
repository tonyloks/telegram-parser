"""
Файл: env_config_handler.py

Назначение:
    Работа с пользовательскими данными (API_ID, API_HASH) через .env файл с использованием pydantic-модели UserEnvData.

Основные компоненты:

Классы:
    - UserEnvData(BaseModel):
        Pydantic-модель для хранения API_ID и API_HASH.

Функции:
    - get_user_data() -> UserEnvData | None:
        Чтение API_ID и API_HASH из .env, возврат модели UserEnvData или None.
    - setup_user_data(user_data: UserEnvData) -> None:
        Сохраняет API_ID и API_HASH из модели UserEnvData в .env без пользовательского ввода.

Константы:
    - ENV_PATH: str = ".env"
        Путь к .env-файлу.

Зависимости:
    - os
    - logging
    - python-dotenv
    - pydantic
    - config.logger (get_logger)
"""

# region Корректировка sys.path для импорта config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# endregion

# region Импорты
import os
import logging
from dotenv import load_dotenv, set_key, dotenv_values
from config.logger import get_logger
# endregion

# region Константы .env
ENV_PATH: str = ".env"
# endregion

# region Логгер
logger = get_logger(__name__)
# endregion

# region Модель данных
from pydantic import BaseModel, Field

class UserEnvData(BaseModel):
    """
    Модель для хранения API_ID и API_HASH пользователя.
    """
    api_id: str = Field(..., description="API_ID Telegram API")
    api_hash: str = Field(..., description="API_HASH Telegram API")
# endregion

# region FUNCTION get_user_data
# CONTRACT
# Args:
#   - None
# Returns:
#   - UserEnvData | None: Модель с api_id и api_hash или None, если не найдено
# Side Effects:
#   - Чтение файла .env
# Raises:
#   - None (ошибки логируются, возвращается None)
def get_user_data() -> UserEnvData | None:
    """
    Читает API_ID и API_HASH из .env и возвращает UserEnvData.
    """
    logger.info("[START_FUNCTION][get_user_data] Чтение .env")
    load_dotenv(ENV_PATH, override=True)
    values = dotenv_values(ENV_PATH)
    api_id = values.get("API_ID")
    api_hash = values.get("API_HASH")
    logger.info(f"[get_user_data][Результат] API_ID: {api_id}, API_HASH: {api_hash}")
    logger.info("[END_FUNCTION][get_user_data] Успешно")
    if api_id and api_hash:
        return UserEnvData(api_id=api_id, api_hash=api_hash)
    return None
# endregion FUNCTION get_user_data

# region FUNCTION setup_user_data
# CONTRACT
# Args:
#   - user_data: UserEnvData — данные для сохранения в .env
# Returns:
#   - None
# Side Effects:
#   - Запись API_ID и API_HASH в .env
# Raises:
#   - None (ошибки логируются)
def setup_user_data(user_data: UserEnvData) -> None:
    """
    Сохраняет API_ID и API_HASH в .env без пользовательского ввода.
    """
    logger.info("[START_FUNCTION][setup_user_data] Сохранение API_ID и API_HASH в .env")
    set_key(ENV_PATH, "API_ID", user_data.api_id)
    logger.info(f"[setup_user_data][Изменение] обновлен API_ID: {user_data.api_id}")
    set_key(ENV_PATH, "API_HASH", user_data.api_hash)
    logger.info(f"[setup_user_data][Изменение] обновлен API_HASH: {user_data.api_hash}")
    logger.info("[END_FUNCTION][setup_user_data] Данные сохранены")
# endregion FUNCTION setup_user_data

# region Точка входа
if __name__ == "__main__":
    logger.info("[START_MAIN] Запуск env_config_handler")
    # Тест функции get_user_data
    user = get_user_data()
    logger.info(f"[MAIN][user] {user}")

    # Тест функции setup_user_data
    setup_user_data(UserEnvData(api_id="12345", api_hash="hashval"))
    logger.info("[END_MAIN] Завершение env_config_handler")
# endregion 