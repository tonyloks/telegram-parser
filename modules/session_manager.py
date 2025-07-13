"""
Файл: session_manager.py

Назначение:
    Управление сессией пользователя Telegram через Telethon. Хранение и восстановление сессии из файла SQLite в папке 'sessions'.
    Для получения api_id, api_hash и phone_number используется env_config_handler (чтение из .env через pydantic-модель UserEnvData).

Основные компоненты (будут добавлены):

Классы:
    - SessionManager: Класс для управления жизненным циклом сессии Telethon (создание, получение, удаление).

Функции:
    - create_session() -> TelegramClient:
        Создает новую сессию Telethon, используя api_id и api_hash из env_config_handler, файл сессии сохраняется в 'sessions/'.
    - get_session() -> TelegramClient | None:
        Возвращает TelegramClient, если сессия существует.
    - remove_session() -> None:
        Удаляет файл сессии пользователя из 'sessions/'.

Константы:
    - SESSION_DIR: str = 'sessions'
        Папка для хранения файлов сессий.
    - SESSION_FILE_EXT: str = '.session'
        Расширение файлов сессий.

Зависимости:
    - telethon
    - pydantic
    - logging (используется общий логгер из config)
    - handlers.env_config_handler (UserEnvData, get_user_data)

Требования к API:
    - Для создания сессии необходимы api_id, api_hash и phone_number, получаемые через env_config_handler из .env (см. handlers/env_config_handler.py)
"""

# region Корректировка sys.path для импорта
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# endregion

# region Импорты
import os
import asyncio
from telethon import TelegramClient
from config.logger import get_logger
from handlers.env_config_handler import get_user_data, UserEnvData
# endregion

# region Логгер
logger = get_logger(__name__)
# endregion

# region Константы
SESSION_DIR = Path('sessions')
SESSION_DIR.mkdir(exist_ok=True) # Создаем папку, если ее нет
# endregion

# region Класс SessionManager
class SessionManager:
    """
    Управляет сессиями Telethon.
    """
    def __init__(self, user_data: UserEnvData):
        """
        Инициализирует менеджер сессий.

        Args:
            user_data: Данные пользователя (api_id, api_hash, phone_number).
        """
        self.user_data = user_data
        self.session_name = f"{self.user_data.phone_number.replace('+', '')}"
        self.session_path = SESSION_DIR / f"{self.session_name}.session"
        self.client = TelegramClient(str(self.session_path), self.user_data.api_id, self.user_data.api_hash)
        logger.info(f"[SessionManager][INIT] Менеджер сессий для {self.session_name} инициализирован.")

    # region FUNCTION connect
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: Подключается к Telegram.
    # Raises: Exception on connection failure.
    async def connect(self):
        """Подключает клиента Telegram."""
        logger.info(f"[START_FUNCTION][connect] Подключение клиента {self.session_name}")
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.warning(f"[connect] Пользователь {self.session_name} не авторизован. Попытка входа.")
                await self.client.send_code_request(self.user_data.phone_number)
                # Код подтверждения нужно будет ввести в консоли
                await self.client.sign_in(self.user_data.phone_number, input('Введите код подтверждения: '))
            logger.info(f"[END_FUNCTION][connect] Клиент {self.session_name} успешно подключен.")
        except Exception as e:
            logger.error(f"[connect][ERROR] Не удалось подключить клиента: {e}")
            raise

    # endregion FUNCTION connect

    # region FUNCTION disconnect
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: Отключается от Telegram.
    async def disconnect(self):
        """Отключает клиента Telegram."""
        logger.info(f"[START_FUNCTION][disconnect] Отключение клиента {self.session_name}")
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info(f"[END_FUNCTION][disconnect] Клиент {self.session_name} отключен.")
        else:
            logger.info(f"[disconnect] Клиент {self.session_name} уже был отключен.")
    # endregion FUNCTION disconnect
    
    # region FUNCTION get_session_client
    # CONTRACT
    # Args: None
    # Returns: TelegramClient - экземпляр клиента.
    def get_session_client(self) -> TelegramClient:
        """Возвращает экземпляр TelegramClient."""
        logger.info(f"[get_session_client] Возвращен клиент для сессии {self.session_name}")
        return self.client
    # endregion FUNCTION get_session_client

    # region FUNCTION remove_session
    # CONTRACT
    # Args: None
    # Returns: bool - True, если сессия удалена, иначе False.
    # Side Effects: Удаляет файл сессии.
    def remove_session(self) -> bool:
        """Удаляет файл сессии."""
        logger.info(f"[START_FUNCTION][remove_session] Удаление сессии {self.session_name}")
        if self.session_path.exists():
            try:
                self.session_path.unlink()
                logger.info(f"[END_FUNCTION][remove_session] Сессия {self.session_name} удалена.")
                return True
            except OSError as e:
                logger.error(f"[remove_session][ERROR] Ошибка при удалении файла сессии: {e}")
                return False
        else:
            logger.warning(f"[remove_session] Файл сессии {self.session_path} не найден.")
            return False
    # endregion FUNCTION remove_session

# endregion Класс SessionManager

# region Точка входа
if __name__ == "__main__":
    # Для тестов необходимо, чтобы .env файл был настроен
    # Можно использовать setup_user_data из env_config_handler для его создания
    # from handlers.env_config_handler import setup_user_data
    # setup_user_data(UserEnvData(api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", phone_number="YOUR_PHONE"))

    async def main():
        logger.info("[START_MAIN] Тестирование SessionManager")
        
        # region Получаем данные пользователя из .env через get_user_data
        from handlers.env_config_handler import get_user_data
        user_env_data = get_user_data()
        if user_env_data is None:
            logger.error("[MAIN][ERROR] Не удалось получить данные пользователя из .env. Проверьте файл .env.")
            return
        # endregion

        session_manager = SessionManager(user_env_data)

        # 1. Подключение
        await session_manager.connect()

        # 2. Получение клиента и вывод информации о себе
        client = session_manager.get_session_client()
        if await client.is_user_authorized():
            me = await client.get_me()
            logger.info(f"[MAIN][INFO] Информация о пользователе: {me.first_name} {me.last_name}")
        
        # 3. Отключение
        await session_manager.disconnect()

        # 4. Удаление сессии (раскомментируйте для теста)
        # if session_manager.remove_session():
        #     logger.info("[MAIN][INFO] Файл сессии успешно удален.")

        logger.info("[END_MAIN] Тестирование SessionManager завершено.")

    # Запуск асинхронной функции main
    # Используем asyncio.run() для Python 3.7+
    try:
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        # В некоторых средах (например, Jupyter/IPython) asyncio.run может вызывать ошибку,
        # если цикл событий уже запущен. Используем альтернативный подход.
        logger.warning(f"Ошибка при запуске asyncio.run: {e}. Попытка альтернативного запуска.")
        loop = asyncio.get_event_loop()
        if loop.is_running():
            task = loop.create_task(main())
        else:
            loop.run_until_complete(main())
# endregion 