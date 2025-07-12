"""
Файл: yaml_config_handler.py

Назначение:
    Работа с конфигурацией приложения в формате YAML.
    - Чтение, сохранение и интерактивная настройка параметров выгрузки (config/config.yaml)

Основные компоненты:

Функции:
    - get_config() -> dict:
        Чтение параметров из config/config.yaml.
    - save_config(config: dict) -> None:
        Сохранение параметров в config/config.yaml.
    - setup_config() -> None:
        Интерактивное меню для настройки параметров выгрузки.

Константы:
    - CONFIG_PATH: str = "config/config.yaml"
        Путь к YAML-конфигу.

Зависимости:
    - os
    - logging
    - yaml (PyYAML)
"""

# region Импорты
import os
import logging
import yaml
from config.logger import get_logger
# endregion

# region Константы
CONFIG_PATH: str = "config/config.yaml"
# endregion

# region Логгер
logger = get_logger(__name__)
# endregion

# region FUNCTION get_config
# CONTRACT
# Args:
#   - None
# Returns:
#   - dict: Словарь с параметрами из config.yaml
# Side Effects:
#   - Чтение файла config/config.yaml
# Raises:
#   - FileNotFoundError, yaml.YAMLError

def get_config() -> dict:
    """
    Читает параметры из config/config.yaml.
    """
    logger.info("[START_FUNCTION][get_config] Чтение конфига")
    if not os.path.exists(CONFIG_PATH):
        logger.warning("[get_config][Проверка файла] Файл не найден: %s", CONFIG_PATH)
        logger.info("[END_FUNCTION][get_config] Возврат пустого словаря")
        return {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
            logger.info(f"[get_config][Чтение файла] Прочитан конфиг: {config}")
            logger.info("[END_FUNCTION][get_config] Успешно")
            return config
    except Exception as e:
        logger.error(f"[get_config][Ошибка] Ошибка чтения {CONFIG_PATH}: {e}")
        logger.info("[END_FUNCTION][get_config] Ошибка")
        raise
# endregion FUNCTION get_config

# region FUNCTION save_config
# CONTRACT
# Args:
#   - config: dict — параметры для сохранения
# Returns:
#   - None
# Side Effects:
#   - Запись в файл config/config.yaml
# Raises:
#   - OSError, yaml.YAMLError

def save_config(config: dict) -> None:
    """
    Сохраняет параметры в config/config.yaml.
    """
    logger.info(f"[START_FUNCTION][save_config] Сохранение конфига: {config}")
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, allow_unicode=True)
    logger.info("[END_FUNCTION][save_config] Конфиг сохранён")
# endregion FUNCTION save_config

# region FUNCTION setup_config
# CONTRACT
# Args:
#   - None
# Returns:
#   - None
# Side Effects:
#   - Ввод/вывод в консоль, чтение/запись файла
# Raises:
#   - FileNotFoundError, OSError, yaml.YAMLError

def setup_config() -> None:
    logger.info("[START_FUNCTION][setup_config] Запуск интерактивной настройки")
    while True:
        os.system('cls||clear')
        config = get_config()
        config.setdefault('api_id', None)
        config.setdefault('api_hash', None)
        config.setdefault('parse_user_id', True)
        config.setdefault('parse_user_name', True)
        print(f"1 - Обновить api_id [{config['api_id']}]")
        print(f"2 - Обновить api_hash [{config['api_hash']}]")
        print(f"3 - Парсить user-id [{config['parse_user_id']}]")
        print(f"4 - Парсить user-name [{config['parse_user_name']}]")
        print("e - Выход")
        key = input("Ввод: ")
        logger.info(f"[setup_config][Меню] выбран пункт: {key}")
        if key == '1':
            os.system('cls||clear')
            config['api_id'] = input("Введите API_ID: ")
            logger.info(f"[setup_config][Изменение] обновлен api_id: {config['api_id']}")
        elif key == '2':
            os.system('cls||clear')
            config['api_hash'] = input("Введите API_HASH: ")
            logger.info(f"[setup_config][Изменение] обновлен api_hash: {config['api_hash']}")
        elif key == '3':
            config['parse_user_id'] = not config.get('parse_user_id', True)
            logger.info(f"[setup_config][Изменение] переключен parse_user_id: {config['parse_user_id']}")
        elif key == '4':
            config['parse_user_name'] = not config.get('parse_user_name', True)
            logger.info(f"[setup_config][Изменение] переключен parse_user_name: {config['parse_user_name']}")
        elif key == 'e':
            os.system('cls||clear')
            logger.info("[END_FUNCTION][setup_config] Выход из настройки")
            break
        save_config(config)
        logger.info("[setup_config][Сохранение] параметры сохранены")
# endregion FUNCTION setup_config 

# region Точка входа
if __name__ == "__main__":
    print("Тест get_config():", get_config())
    test_config = {'api_id': 42, 'api_hash': 'test', 'parse_user_id': False, 'parse_user_name': True}
    save_config(test_config)
    print("Тест после save_config():", get_config())
    # setup_config()  # Раскомментируй для ручного теста интерактивного меню
# endregion 