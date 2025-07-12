"""
Файл: env_config_handler.py

Назначение:
    Работа с пользовательскими данными (API_ID, API_HASH) через .env файл.

Основные компоненты:

Функции:
    - get_user_data() -> dict:
        Чтение API_ID и API_HASH из .env.
    - setup_user_data() -> None:
        Интерактивное меню для настройки API_ID и API_HASH в .env.

Константы:
    - ENV_PATH: str = ".env"
        Путь к .env-файлу.

Зависимости:
    - os
    - logging
    - python-dotenv
"""

# region Импорты
import os
import logging
from dotenv import load_dotenv, set_key, dotenv_values
from config.logger import get_logger
# endregion

# region Корректировка sys.path для импорта config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# endregion

# region Константы .env
ENV_PATH: str = ".env"
# endregion

# region Логгер
logger = get_logger(__name__)
# endregion

# region FUNCTION get_user_data
# CONTRACT
# Args:
#   - None
# Returns:
#   - dict: {'api_id': str|None, 'api_hash': str|None}
# Side Effects:
#   - Чтение файла .env
# Raises:
#   - None (ошибки логируются, возвращается None)
def get_user_data() -> dict:
    """
    Читает API_ID и API_HASH из .env.
    """
    logger.info("[START_FUNCTION][get_user_data] Чтение .env")
    load_dotenv(ENV_PATH, override=True)
    values = dotenv_values(ENV_PATH)
    api_id = values.get("API_ID")
    api_hash = values.get("API_HASH")
    logger.info(f"[get_user_data][Результат] API_ID: {api_id}, API_HASH: {api_hash}")
    logger.info("[END_FUNCTION][get_user_data] Успешно")
    return {"api_id": api_id, "api_hash": api_hash}
# endregion FUNCTION get_user_data

# region FUNCTION setup_user_data
# CONTRACT
# Args:
#   - None
# Returns:
#   - None
# Side Effects:
#   - Ввод/вывод в консоль, чтение/запись .env
# Raises:
#   - None (ошибки логируются)
def setup_user_data() -> None:
    """
    Интерактивная настройка API_ID и API_HASH в .env.
    """
    logger.info("[START_FUNCTION][setup_user_data] Запуск настройки .env")
    while True:
        os.system('cls||clear')
        user_data = get_user_data()
        print(f"1 - Обновить API_ID [{user_data['api_id']}]")
        print(f"2 - Обновить API_HASH [{user_data['api_hash']}]")
        print("e - Выход")
        key = input("Ввод: ")
        logger.info(f"[setup_user_data][Меню] выбран пункт: {key}")
        if key == '1':
            os.system('cls||clear')
            api_id = input("Введите API_ID: ")
            set_key(ENV_PATH, "API_ID", api_id)
            logger.info(f"[setup_user_data][Изменение] обновлен API_ID: {api_id}")
        elif key == '2':
            os.system('cls||clear')
            api_hash = input("Введите API_HASH: ")
            set_key(ENV_PATH, "API_HASH", api_hash)
            logger.info(f"[setup_user_data][Изменение] обновлен API_HASH: {api_hash}")
        elif key == 'e':
            os.system('cls||clear')
            logger.info("[END_FUNCTION][setup_user_data] Выход из настройки .env")
            break
# endregion FUNCTION setup_user_data

# region Точка входа
if __name__ == "__main__":
    logger.info("[START_MAIN] Запуск env_config_handler")
    # Тест функции get_user_data
    get_user_data()

    # Тест функции setup_user_data
    setup_user_data()
    logger.info("[END_MAIN] Завершение env_config_handler")
# endregion 