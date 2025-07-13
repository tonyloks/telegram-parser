"""
Файл: telegram_client.py

Назначение:
    Предоставляет класс-клиент для взаимодействия с API Telegram с использованием библиотеки Telethon.
    Управляет сессиями, подключением и выполнением основных операций, таких как получение данных.

Основные компоненты:

Классы:
    - TelegramClient: Основной класс для работы с Telegram.

Функции:
    - __init__(self, session_name: str, api_id: int, api_hash: str):
        Инициализирует клиент.
    - connect(self) -> None:
        Устанавливает и авторизует сессию.
    - disconnect(self) -> None:
        Безопасно разрывает соединение.
    - get_dialogs(self) -> list:
        Получает список диалогов пользователя.

Зависимости:
    - telethon
    - config.logger
"""

# region Корректировка sys.path для импорта
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# endregion


# region Импорты
import asyncio
from telethon.sync import TelegramClient as TelethonSyncClient
from telethon.errors import SessionPasswordNeededError
from config.logger import get_logger
# endregion

# region Инициализация логгера
logger = get_logger(__name__)
# endregion

# region Класс TelegramClient
class TelegramClient:
    """
    Клиент для взаимодействия с API Telegram.
    """

    # region FUNCTION __init__
    # CONTRACT
    # Args:
    #   - session_name: Имя файла сессии (без расширения).
    #   - api_id: API ID, полученный от Telegram.
    #   - api_hash: API Hash, полученный от Telegram.
    #   - session_path: Путь к папке с сессиями.
    # Returns:
    #   - None
    # Side Effects:
    #   - Создает экземпляр клиента Telethon.
    def __init__(self, session_name: str, api_id: int, api_hash: str, session_path: str = "sessions/"):
        """
        Инициализирует асинхронный клиент Telethon.
        """
        logger.info(f"[START_FUNCTION][__init__] Инициализация клиента для сессии '{session_name}'")
        self.session_path = f"{session_path}{session_name}.session"
        self.client = TelethonSyncClient(self.session_path, api_id, api_hash)
        logger.info(f"[END_FUNCTION][__init__] Клиент для сессии '{session_name}' инициализирован")
    # endregion FUNCTION __init__

    # region FUNCTION connect
    # CONTRACT
    # Args:
    #   - None
    # Returns:
    #   - None
    # Side Effects:
    #   - Выполняет подключение к серверам Telegram.
    #   - Может запрашивать пароль двухфакторной аутентификации в консоли.
    # Raises:
    #   - Exception: при ошибке подключения.
    async def connect(self) -> None:
        """
        Устанавливает соединение с Telegram.
        """
        logger.info(f"[START_FUNCTION][connect] Попытка подключения для сессии '{self.session_path}'")
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.warning(f"Сессия '{self.session_path}' не авторизована. Потребуется вход.")
                # Сюда можно добавить логику для входа по номеру телефона, если требуется
            logger.info(f"Подключение для сессии '{self.session_path}' успешно установлено.")
        except Exception as e:
            logger.error(f"[connect] Ошибка подключения для сессии '{self.session_path}': {e}")
            raise
        logger.info(f"[END_FUNCTION][connect] Процесс подключения завершен для сессии '{self.session_path}'")
    # endregion FUNCTION connect

    # region FUNCTION disconnect
    # CONTRACT
    # Args:
    #   - None
    # Returns:
    #   - None
    # Side Effects:
    #   - Разрывает соединение с Telegram.
    async def disconnect(self) -> None:
        """
        Разрывает соединение с Telegram.
        """
        logger.info(f"[START_FUNCTION][disconnect] Отключение сессии '{self.session_path}'")
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info(f"Сессия '{self.session_path}' успешно отключена.")
        else:
            logger.info(f"Сессия '{self.session_path}' уже была отключена.")
        logger.info(f"[END_FUNCTION][disconnect] Процесс отключения завершен для сессии '{self.session_path}'")
    # endregion FUNCTION disconnect

    # region FUNCTION get_dialogs
    # CONTRACT
    # Args:
    #   - None
    # Returns:
    #   - list: Список диалогов (чатов, каналов, пользователей).
    # Side Effects:
    #   - Выполняет API-запрос к Telegram.
    # Raises:
    #   - Exception: если клиент не подключен или возникает ошибка API.
    async def get_dialogs(self) -> list:
        """
        Асинхронно получает список всех диалогов.
        """
        logger.info(f"[START_FUNCTION][get_dialogs] Запрос списка диалогов для сессии '{self.session_path}'")
        if not self.client.is_connected():
            logger.error("[get_dialogs] Клиент не подключен. Сначала вызовите connect().")
            raise ConnectionError("Клиент не подключен.")

        try:
            dialogs = await self.client.get_dialogs()
            logger.info(f"[get_dialogs] Получено {len(dialogs)} диалогов.")
            return dialogs
        except Exception as e:
            logger.error(f"[get_dialogs] Ошибка при получении диалогов: {e}")
            raise
        finally:
            logger.info(f"[END_FUNCTION][get_dialogs] Запрос списка диалогов завершен.")
    # endregion FUNCTION get_dialogs

# endregion Класс TelegramClient

# region Пример использования
async def main():
    """
    Пример использования TelegramClient.
    Для запуска этого блока напрямую, убедитесь, что конфигурация (api_id, api_hash) доступна.
    """
    logger.info("Запуск примера использования TelegramClient")

    from handlers.env_config_handler import get_user_data
    user_env_data = get_user_data()

    client = TelegramClient(session_name=user_env_data.phone_number, api_id=user_env_data.api_id, api_hash=user_env_data.api_hash)

    try:
        await client.connect()
        dialogs = await client.get_dialogs()
        for i, dialog in enumerate(dialogs[:10]):  # Показываем первые 10 диалогов
            logger.info(f"{i+1}. {dialog.name} (ID: {dialog.id})")
    except Exception as e:
        logger.error(f"В ходе выполнения примера произошла ошибка: {e}")
    finally:
        await client.disconnect()
        logger.info("Пример использования TelegramClient завершен")


if __name__ == "__main__":
    # Для прямого запуска этого файла
    # python -m modules.telegram_client
    asyncio.run(main())
# endregion 