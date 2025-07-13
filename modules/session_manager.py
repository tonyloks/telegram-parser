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
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
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

# region Функции
def _get_session_path(phone_number: str) -> Path:
    """
    Возвращает стандартизированный путь к файлу сессии.
    """
    SESSION_DIR.mkdir(exist_ok=True)
    return SESSION_DIR / f"{phone_number.lstrip('+')}.session"
# endregion Функции

# region Класс SessionManager
class SessionManager:
    """
    Управляет сессиями Telethon: создание, авторизация, удаление.
    """

    # region METHOD __init__
    # CONTRACT
    # Args:
    #   - user_data: UserEnvData — данные пользователя (api_id, api_hash, phone_number).
    # Returns:
    #   - None
    # Side Effects:
    #   - Инициализирует клиент Telethon.
    # Raises:
    #   - ValueError: если api_id или api_hash отсутствуют.
    def __init__(self, user_data: UserEnvData):
        """
        Инициализирует менеджер сессий.
        """
        if not user_data.api_id or not user_data.api_hash:
            raise ValueError("API_ID и API_HASH должны быть предоставлены.")

        self.user_data = user_data
        self.phone_number = user_data.phone_number.lstrip('+')
        self.session_path = _get_session_path(user_data.phone_number)

        self.client = TelegramClient(
            StringSession(),  # Используем StringSession для временного хранения
            int(self.user_data.api_id),
            self.user_data.api_hash,
            device_model="PC",
            system_version="Windows 10",
            app_version="1.0.0",
            lang_code="ru",
            system_lang_code="ru"
        )

        logger.info(f"[SessionManager][INIT] Менеджер сессий для {self.phone_number} инициализирован.")
    # endregion METHOD __init__

    # region METHOD start_auth
    # CONTRACT
    # Args: None
    # Returns: str — phone_code_hash, необходимый для завершения авторизации
    # Side Effects: Отправляет код подтверждения на телефон пользователя
    # Raises: Exception при ошибке отправки кода
    async def start_auth(self) -> str:
        """
        Начинает процесс авторизации, отправляя код на номер телефона.
        """
        logger.info(f"[START_FUNCTION][start_auth] Отправка кода на {self.user_data.phone_number}")
        await self.client.connect()
        if not await self.client.is_user_authorized():
            sent_code = await self.client.send_code_request(self.user_data.phone_number)
            phone_code_hash = sent_code.phone_code_hash
            logger.info(f"[END_FUNCTION][start_auth] Код отправлен, hash: {phone_code_hash}")
            return phone_code_hash
        raise RuntimeError("Клиент уже авторизован.")
    # endregion METHOD start_auth

    # region METHOD finish_auth
    # CONTRACT
    # Args:
    #   - phone_code: str — код подтверждения из Telegram
    #   - phone_code_hash: str — hash, полученный на этапе start_auth
    #   - password: str | None — пароль для двухфакторной аутентификации (если требуется)
    # Returns: None
    # Side Effects:
    #   - Завершает авторизацию и сохраняет сессию в файл.
    #   - Отключает клиент.
    # Raises:
    #   - SessionPasswordNeededError: если требуется 2FA пароль.
    async def finish_auth(self, phone_code: str, phone_code_hash: str, password: str = None) -> None:
        """
        Завершает процесс авторизации с помощью кода и, возможно, пароля.
        """
        logger.info(f"[START_FUNCTION][finish_auth] Попытка завершения авторизации для {self.phone_number}")
        
        # Гарантируем, что клиент подключен перед отправкой запроса
        if not self.client.is_connected():
            await self.client.connect()

        try:
            await self.client.sign_in(
                self.user_data.phone_number,
                phone_code,
                phone_code_hash=phone_code_hash
            )
        except SessionPasswordNeededError:
            if not password:
                logger.warning("[finish_auth] Требуется пароль двухфакторной аутентификации, но он не предоставлен.")
                raise
            await self.client.sign_in(password=password)

        if await self.client.is_user_authorized():
            # Сохраняем строку сессии в файл
            session_string = self.client.session.save()
            with self.session_path.open("w", encoding="utf-8") as f:
                f.write(session_string)
            logger.info(f"[END_FUNCTION][finish_auth] Сессия для {self.phone_number} успешно сохранена в файл.")
        else:
            logger.error("[finish_auth] Авторизация не удалась.")

        await self.client.disconnect()
    # endregion METHOD finish_auth

    # region FUNCTION connect
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: Подключается к Telegram.
    # Raises: Exception on connection failure.
    async def connect(self):
        """[УСТАРЕЛО] Подключает клиента Telegram. Используйте start_auth/finish_auth для web-интерфейса."""
        logger.info(f"[START_FUNCTION][connect] Подключение клиента {self.phone_number}")
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logger.warning(f"[connect] Пользователь {self.phone_number} не авторизован. Попытка входа.")
                sent_code = await self.client.send_code_request(self.user_data.phone_number)
                phone_code_hash = sent_code.phone_code_hash
                # Код подтверждения нужно будет ввести в консоли
                await self.client.sign_in(self.user_data.phone_number, input('Введите код подтверждения: '), phone_code_hash=phone_code_hash)
            logger.info(f"[END_FUNCTION][connect] Клиент {self.phone_number} успешно подключен.")
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
        logger.info(f"[START_FUNCTION][disconnect] Отключение клиента {self.phone_number}")
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info(f"[END_FUNCTION][disconnect] Клиент {self.phone_number} отключен.")
        else:
            logger.info(f"[disconnect] Клиент {self.phone_number} уже был отключен.")
    # endregion FUNCTION disconnect
    
    # region FUNCTION get_session_client
    # CONTRACT
    # Args: None
    # Returns: TelegramClient - экземпляр клиента.
    def get_session_client(self) -> TelegramClient:
        """Возвращает экземпляр TelegramClient."""
        logger.info(f"[get_session_client] Возвращен клиент для сессии {self.phone_number}")
        return self.client
    # endregion FUNCTION get_session_client

    # region FUNCTION remove_session
    # CONTRACT
    # Args: None
    # Returns: bool - True, если сессия удалена, иначе False.
    # Side Effects: Удаляет файл сессии.
    def remove_session(self) -> bool:
        """Удаляет файл сессии."""
        logger.info(f"[START_FUNCTION][remove_session] Удаление сессии {self.phone_number}")
        if self.session_path.exists():
            try:
                self.session_path.unlink()
                logger.info(f"[END_FUNCTION][remove_session] Сессия {self.phone_number} удалена.")
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
        logger.info(f"[START_FUNCTION][session_exists] Проверка наличия сессии {self.phone_number}")
        exists = self.session_path.exists()
        logger.info(f"[END_FUNCTION][session_exists] Сессия {self.phone_number} существует: {exists}")
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