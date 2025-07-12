"""
Файл: logger.py

Назначение:
    Конфигурация и инициализация логгера для всего проекта с интеграцией logfire.
    API-ключ logfire берётся из переменной окружения LOGFIRE_API_KEY.

Основные компоненты:

Функции:
    - get_logger(name: str) -> logging.Logger:
        Возвращает настроенный логгер с интеграцией logfire.

Константы:
    - LOG_FORMAT: str
        Формат логов.
    - LOG_LEVEL: int
        Уровень логирования по умолчанию.
    - Переменная окружения LOGFIRE_API_KEY
        API-ключ для logfire (обязателен).

Зависимости:
    - logging
    - logfire
    - os (для доступа к переменным окружения)
"""

# region Импорты
import logging
import logfire
import os
# endregion

# region Константы
LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(pathname)s:%(lineno)d | %(funcName)s | %(message)s"
LOG_LEVEL: int = logging.INFO
# endregion

# region FUNCTION get_logger
# CONTRACT
# Args:
#   - name: Имя логгера (обычно __name__ модуля).
# Returns:
#   - logging.Logger: Настроенный логгер (с интеграцией logfire, если есть ключ).
# Side Effects:
#   - Инициализация logfire с API-ключом из переменной окружения LOGFIRE_API_KEY (если есть), настройка basicConfig.
# Raises:
#   - None

def get_logger(name: str) -> logging.Logger:
    """
    Возвращает настроенный логгер с интеграцией logfire, если задан API-ключ.
    Если переменная окружения LOGFIRE_API_KEY отсутствует — logfire не используется.
    """
    api_key = os.environ.get("LOGFIRE_API_KEY")
    if api_key:
        logfire.configure(token=api_key)
        handlers = [logging.StreamHandler(), logfire.LogfireLoggingHandler()]
    else:
        handlers = [logging.StreamHandler()]
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=handlers)
    logger = logging.getLogger(name)
    return logger
# endregion FUNCTION get_logger 

# region Тест логгера
if __name__ == "__main__":
    logger = get_logger("test_logger")
    logger.info("[TEST][INFO] Проверка info-сообщения логгера")
    logger.error("[TEST][ERROR] Проверка error-сообщения логгера")
# endregion 