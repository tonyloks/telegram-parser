"""
Файл: session_manager.py

Назначение:
    Управление сессией пользователя Telegram через Telethon. Хранение и восстановление сессии из файла SQLite в папке 'sessions'.
    Для получения api_id, api_hash и phone_number используется env_config_handler (чтение из .env через pydantic-модель UserEnvData).
    
    ВАЖНО: session_name формируется из phone_number пользователя с удалённым символом '+'. Файл сессии ищется и создаётся по имени <номер_без_плюса>.session в папке 'sessions'.

Основные компоненты:

Классы:
    - SessionManager: Класс для управления жизненным циклом сессии Telethon (создание, получение, удаление, проверка существования).

Функции:
    - create_session() -> TelegramClient:
        Создает новую сессию Telethon, используя api_id и api_hash из env_config_handler, файл сессии сохраняется в 'sessions/'.
    - get_session() -> TelegramClient | None:
        Возвращает TelegramClient, если сессия существует.
    - remove_session() -> None:
        Удаляет файл сессии пользователя из 'sessions/'.
    - session_exists() -> bool:
        Проверяет, существует ли файл сессии для пользователя (по номеру без '+').

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
        Создает сессию, если она не существует с помощью TelegramClient.

        Args:
            user_data: Данные пользователя (api_id, api_hash, phone_number).
        """
        self.user_data = user_data
        self.session_name = f"{self.user_data.phone_number.replace('+', '')}"
        self.session_path = SESSION_DIR / f"{self.session_name}.session"
        self.client = TelegramClient(str(self.session_path), self.user_data.api_id, self.user_data.api_hash)
        logger.info(f"[SessionManager][INIT] Менеджер сессий для {self.session_name} инициализирован.")

    # region FUNCTION start_auth
    # CONTRACT
    # Args: None
    # Returns: str — phone_code_hash, необходимый для завершения авторизации
    # Side Effects: Отправляет код подтверждения на телефон пользователя
    # Raises: Exception при ошибке отправки кода
    async def start_auth(self) -> str:
        """
        Отправляет код подтверждения на телефон пользователя и возвращает phone_code_hash.
        """
        logger.info(f"[START_FUNCTION][start_auth] Отправка кода на {self.user_data.phone_number}")
        await self.client.connect()
        sent_code = await self.client.send_code_request(self.user_data.phone_number)
        phone_code_hash = sent_code.phone_code_hash
        logger.info(f"[END_FUNCTION][start_auth] Код отправлен, hash: {phone_code_hash}")
        return phone_code_hash
    # endregion FUNCTION start_auth

    # region FUNCTION finish_auth
    # CONTRACT
    # Args:
    #   - code: str — код подтверждения из Telegram
    #   - phone_code_hash: str — hash, полученный на этапе start_auth
    # Returns: None
    # Side Effects: Завершает авторизацию пользователя
    # Raises: Exception при ошибке авторизации
    async def finish_auth(self, code: str, phone_code_hash: str) -> None:
        """
        Завершает авторизацию пользователя по коду и hash.
        """
        logger.info(f"[START_FUNCTION][finish_auth] Завершение авторизации для {self.user_data.phone_number}")
        await self.client.sign_in(self.user_data.phone_number, code, phone_code_hash=phone_code_hash)
        logger.info(f"[END_FUNCTION][finish_auth] Авторизация завершена")
    # endregion FUNCTION finish_auth

    # region FUNCTION connect
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: Подключается к Telegram.
    # Raises: Exception on connection failure.
    async def connect(self):
        """[УСТАРЕЛО] Подключает клиента Telegram. Используйте start_auth/finish_auth для web-интерфейса."""
        logger.info(f"[START_FUNCTION][connect] Подключение клиента {self.session_name}")
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.warning(f"[connect] Пользователь {self.session_name} не авторизован. Попытка входа.")
                sent_code = await self.client.send_code_request(self.user_data.phone_number)
                phone_code_hash = sent_code.phone_code_hash
                # Код подтверждения нужно будет ввести в консоли
                await self.client.sign_in(self.user_data.phone_number, input('Введите код подтверждения: '), phone_code_hash=phone_code_hash)
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

    # region FUNCTION session_exists
    # CONTRACT
    # Args: None
    # Returns: bool - True, если файл сессии существует, иначе False.
    # Side Effects: Нет
    # Raises: Нет
    def session_exists(self) -> bool:
        """
        Проверяет, существует ли файл сессии для текущего пользователя.
        """
        logger.info(f"[START_FUNCTION][session_exists] Проверка наличия сессии {self.session_name}")
        exists = self.session_path.exists()
        logger.info(f"[END_FUNCTION][session_exists] Сессия {self.session_name} существует: {exists}")
        return exists
    # endregion FUNCTION session_exists

    # region FUNCTION session_file_exists
    # CONTRACT
    # Args:
    #   - phone_number: str — номер телефона пользователя (с + или без)
    # Returns:
    #   - bool — True, если файл сессии существует, иначе False
    # Side Effects:
    #   - Нет
    # Raises:
    #   - Нет
    @staticmethod
    def session_file_exists(phone_number: str) -> bool:
        """
        Проверяет, существует ли файл сессии для указанного номера телефона.
        """
        session_name = phone_number.replace('+', '')
        session_path = SESSION_DIR / f"{session_name}.session"
        return session_path.exists()
    # endregion FUNCTION session_file_exists

    # region FUNCTION remove_all_sessions_by_phone
    # CONTRACT
    # Args:
    #   - phone_number: str — номер телефона пользователя (с + или без)
    # Returns:
    #   - int — количество удалённых файлов
    # Side Effects:
    #   - Удаляет все файлы сессий, соответствующие номеру
    # Raises:
    #   - Нет
    @staticmethod
    def remove_all_sessions_by_phone(phone_number: str) -> int:
        """
        Удаляет все файлы сессий для указанного номера телефона (с + и без +) в папке sessions.
        """
        logger = get_logger(__name__)
        logger.info(f"[START_FUNCTION][remove_all_sessions_by_phone] Удаление всех сессий для номера {phone_number}")
        session_variants = [
            phone_number.replace('+', ''),
            phone_number if phone_number.startswith('+') else f'+{phone_number}'
        ]
        removed_count = 0
        for variant in set(session_variants):
            session_file = SESSION_DIR / f"{variant}.session"
            if session_file.exists():
                try:
                    session_file.unlink()
                    removed_count += 1
                    logger.info(f"[remove_all_sessions_by_phone] Удалён файл: {session_file}")
                except Exception as e:
                    logger.error(f"[remove_all_sessions_by_phone][ERROR] Не удалось удалить {session_file}: {e}")
        logger.info(f"[END_FUNCTION][remove_all_sessions_by_phone] Удалено файлов: {removed_count}")
        return removed_count
    # endregion FUNCTION remove_all_sessions_by_phone

# endregion Класс SessionManager

# region Точка входа
if __name__ == "__main__":
    # region Тест: проверка существования сессии
    import asyncio
    from handlers.env_config_handler import get_user_data
    user_env_data = get_user_data()
    if user_env_data is None:
        logger.error("[MAIN][ERROR] Не удалось получить данные пользователя из .env. Проверьте файл .env.")
    else:
        session_manager = SessionManager(user_env_data)
        exists = session_manager.session_exists()
        logger.info(f"[MAIN][TEST] Сессия для {user_env_data.phone_number} существует: {exists}")
    # endregion
# endregion 