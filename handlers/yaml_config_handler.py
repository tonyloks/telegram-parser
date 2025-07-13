"""
Файл: yaml_config_handler.py

Назначение:
    Работа с конфигурацией приложения в формате YAML (config/config.yaml) с использованием pydantic-модели AppConfigData.

Основные компоненты:

Классы:
    - AppConfigData(BaseModel):
        Pydantic-модель для хранения параметров config.yaml (api_id, api_hash, parse_user_id, parse_user_name).

Функции:
    - get_config() -> AppConfigData | None:
        Чтение параметров из config/config.yaml, возврат модели AppConfigData или None.
    - save_config(config: AppConfigData) -> None:
        Сохраняет параметры из модели AppConfigData в config/config.yaml.

Константы:
    - CONFIG_PATH: str = "config/config.yaml"
        Путь к YAML-конфигу.

Зависимости:
    - os
    - logging
    - yaml (PyYAML)
    - pydantic
    - config.logger (get_logger)
"""

# region Импорты
import os
import logging
import yaml
import sys
from pathlib import Path
# Добавляем корень проекта в sys.path для корректного импорта config
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from config.logger import get_logger
# endregion

# region Корректировка sys.path для импорта config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# endregion

# region Модель данных
from pydantic import BaseModel, Field

class AppConfigData(BaseModel):
    """
    Модель для хранения параметров config.yaml.
    """
    parse_user_id: bool = Field(..., description="Парсить user-id")
    parse_user_name: bool = Field(..., description="Парсить user-name")
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
#   - AppConfigData | None: Модель с параметрами из config.yaml или None
# Side Effects:
#   - Чтение файла config/config.yaml
# Raises:
#   - FileNotFoundError, yaml.YAMLError

def get_config() -> AppConfigData | None:
    """
    Читает параметры из config/config.yaml и возвращает AppConfigData.
    """
    logger.info("[START_FUNCTION][get_config] Чтение конфига")
    if not os.path.exists(CONFIG_PATH):
        logger.warning("[get_config][Проверка файла] Файл не найден: %s", CONFIG_PATH)
        logger.info("[END_FUNCTION][get_config] Возврат None")
        return None
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
            logger.info(f"[get_config][Чтение файла] Прочитан конфиг: {config}")
            logger.info("[END_FUNCTION][get_config] Успешно")
            return AppConfigData(**config)
    except Exception as e:
        logger.error(f"[get_config][Ошибка] Ошибка чтения {CONFIG_PATH}: {e}")
        logger.info("[END_FUNCTION][get_config] Ошибка")
        raise
# endregion FUNCTION get_config

# region FUNCTION save_config
# CONTRACT
# Args:
#   - config: AppConfigData — параметры для сохранения
# Returns:
#   - None
# Side Effects:
#   - Запись в файл config/config.yaml
# Raises:
#   - OSError, yaml.YAMLError

def save_config(config: AppConfigData) -> None:
    """
    Сохраняет параметры в config/config.yaml.
    """
    logger.info(f"[START_FUNCTION][save_config] Сохранение конфига: {config}")
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config.dict(), f, allow_unicode=True)
    logger.info("[END_FUNCTION][save_config] Конфиг сохранён")
# endregion FUNCTION save_config

# region Точка входа
if __name__ == "__main__":
    logger.info("[START_MAIN] Запуск yaml_config_handler")
    # Тест функции get_config
    config = get_config()
    logger.info(f"[MAIN][config] {config}")
    # Тест функции save_config
    save_config(AppConfigData(parse_user_id=True, parse_user_name=False))
    logger.info("[END_MAIN] Завершение yaml_config_handler")
# endregion 