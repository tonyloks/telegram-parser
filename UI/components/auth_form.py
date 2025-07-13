"""
Файл: auth_form.py

Назначение:
    Компонент Streamlit для отображения формы авторизации Telegram API.

Функции:
    - render_auth_menu(): Главная функция-оркестратор для отображения
      и управления формой авторизации.

Зависимости:
    - streamlit
    - handlers.env_config_handler
    - config.logger
    - modules.session_manager
"""

# region Импорты
import streamlit as st
from typing import Optional
from handlers.env_config_handler import (
    get_user_data,
    setup_user_data,
    clear_user_data,
    UserEnvData
)
from config.logger import get_logger
from modules.session_manager import SessionManager
# endregion

logger = get_logger(__name__)

# region FUNCTION _handle_form_submission
# CONTRACT
# Args:
#   - api_id: str — API_ID Telegram API
#   - api_hash: str — API_HASH Telegram API
#   - phone_number: str — номер телефона пользователя
# Returns:
#   - None
# Side Effects:
#   - Сохраняет данные пользователя в .env через setup_user_data
#   - Показывает сообщения через streamlit
#   - Логирует действия
#   - Перезапускает страницу через st.experimental_rerun
# Raises:
#   - None (ошибки отображаются пользователю и логируются)
def _handle_form_submission(api_id: str, api_hash: str, phone_number: str) -> None:
    """
    Обрабатывает логику сохранения данных из формы авторизации.
    """
    if not all([api_id, api_hash, phone_number]):
        st.error("Пожалуйста, заполните все поля.")
        return

    try:
        logger.info(f"Сохранение учетных данных для номера: {phone_number}")
        new_data = UserEnvData(api_id=api_id, api_hash=api_hash, phone_number=phone_number)
        setup_user_data(new_data)
        st.success("Учетные данные успешно сохранены!")
        logger.info("Учетные данные сохранены.")
        st.rerun()
    except Exception as e:
        st.error(f"Ошибка при сохранении данных: {e}")
        logger.error(f"Ошибка сохранения .env: {e}")
# endregion FUNCTION _handle_form_submission

# region FUNCTION _handle_delete_user_data
# CONTRACT
# Args:
#   - None
# Returns:
#   - None
# Side Effects:
#   - Удаляет данные пользователя через clear_user_data
#   - Показывает сообщения через streamlit
#   - Логирует действия
#   - Перезапускает страницу через st.experimental_rerun
# Raises:
#   - None (ошибки отображаются пользователю и логируются)
def _handle_delete_user_data() -> None:
    """
    Удаляет учетные данные пользователя из .env.
    """
    try:
        logger.info("Удаление учетных данных пользователя")
        clear_user_data()
        st.success("Данные пользователя удалены из .env.")
        logger.info("Данные пользователя удалены.")
        st.rerun()
    except Exception as e:
        st.error(f"Ошибка при удалении данных: {e}")
        logger.error(f"Ошибка удаления данных: {e}")
# endregion FUNCTION _handle_delete_user_data


# region FUNCTION _display_auth_form
# CONTRACT
# Args:
#   - user_data: Optional[UserEnvData] — текущие данные пользователя или None
# Returns:
#   - None
# Side Effects:
#   - Отображает форму через streamlit
#   - При сабмите вызывает _handle_form_submission
#   - Кнопка удаления вызывает _handle_delete_user_data
# Raises:
#   - None

def _display_auth_form(user_data: Optional[UserEnvData]) -> None:
    """
    Отображает форму для ввода учетных данных Telegram API.
    """
    with st.form(key="auth_form"):
        st.markdown("##### Учетные данные")
        api_id = st.text_input(
            "API_ID",
            value=user_data.api_id if user_data else "",
            type="password"
        )
        api_hash = st.text_input(
            "API_HASH",
            value=user_data.api_hash if user_data else "",
            type="password"
        )
        phone_number = st.text_input(
            "Номер телефона",
            value=user_data.phone_number if user_data else ""
        )
        submitted = st.form_submit_button("Сохранить данные")
        if submitted:
            _handle_form_submission(api_id, api_hash, phone_number)
    if st.button("Удалить данные", key="delete_user_data", help="Удаляет API_ID, API_HASH, PHONE_NUMBER из .env"):
        _handle_delete_user_data()
# endregion FUNCTION _display_auth_form


# region FUNCTION _display_session_block
# CONTRACT
# Args:
#   - user_data: Optional[UserEnvData] — текущие данные пользователя или None
# Returns:
#   - None
# Side Effects:
#   - Показывает статус сессии и кнопку через streamlit
#   - Удаляет или создает сессию при нажатии кнопки
#   - Логирует действия
#   - Перезапускает страницу через st.experimental_rerun
# Raises:
#   - None (ошибки отображаются пользователю и логируются)
def _display_session_block(user_data: Optional[UserEnvData]) -> None:
    """
    Отдельный блок для статуса сессии и управления сессией (создание/удаление).
    """
    st.markdown("##### Сессия")
    if not user_data:
        st.info("Нет данных пользователя — сессия не может быть определена.")
        return
    phone_number = user_data.phone_number
    session_exists = SessionManager.session_file_exists(phone_number)
    _render_session_status(session_exists, phone_number)
    if session_exists:
        _handle_delete_session_button(phone_number)
    else:
        _handle_create_session_button(user_data)
# endregion FUNCTION _display_session_block

# region FUNCTION _render_session_status
# CONTRACT
# Args:
#   - session_exists: bool — наличие сессии
#   - phone_number: str — номер телефона пользователя
# Returns:
#   - None
# Side Effects:
#   - Показывает статус сессии через streamlit
# Raises:
#   - None

def _render_session_status(session_exists: bool, phone_number: str) -> None:
    """
    Отображает статус сессии для пользователя.
    """
    if session_exists:
        st.success(f"✅ Активная сессия найдена для номера {phone_number}")
    else:
        st.warning(f"Сессия для номера {phone_number} не найдена.")
# endregion FUNCTION _render_session_status


# region FUNCTION _handle_delete_session_button
# CONTRACT
# Args:
#   - phone_number: str — номер телефона пользователя
# Returns:
#   - None
# Side Effects:
#   - Показывает кнопку и сообщения через streamlit
#   - Удаляет сессию при нажатии
#   - Логирует действия
#   - Перезапускает страницу через st.experimental_rerun
# Raises:
#   - None

def _handle_delete_session_button(phone_number: str) -> None:
    """
    Кнопка и логика удаления сессии пользователя.
    """
    if st.button("Удалить сессию", key="delete_session", help="ВНИМАНИЕ: действие необратимо!"):
        try:
            logger.info(f"Удаление сессии для номера: {phone_number}")
            SessionManager.remove_all_sessions_by_phone(phone_number)
            st.success("Все файлы сессии были удалены.")
            logger.info("Сессия удалена.")
            st.rerun()
        except Exception as e:
            st.error(f"Ошибка при удалении сессии: {e}")
            logger.error(f"Ошибка удаления сессии: {e}")
# endregion FUNCTION _handle_delete_session_button

# region FUNCTION _handle_create_session_button
# CONTRACT
# Args:
#   - user_data: UserEnvData — данные пользователя
# Returns:
#   - None
# Side Effects:
#   - Показывает кнопку и сообщения через streamlit
#   - Создает сессию при нажатии
#   - Логирует действия
#   - Перезапускает страницу через st.experimental_rerun
# Raises:
#   - None

def _handle_create_session_button(user_data: UserEnvData) -> None:
    """
    Кнопка и логика создания сессии пользователя (двухэтапная авторизация).
    """
    if 'phone_code_hash' not in st.session_state:
        if st.button("Создать сессию", key="create_session", help="Будет создан файл сессии. Код подтверждения потребуется!"):
            import asyncio
            logger.info(f"Создание сессии для номера: {user_data.phone_number}")
            async def start() -> bool:
                """Запускает процесс авторизации и возвращает True в случае успеха."""
                manager = SessionManager(user_data)
                # Сохраняем менеджер в сессию, чтобы использовать тот же клиент
                st.session_state['session_manager'] = manager
                try:
                    phone_code_hash = await manager.start_auth()
                    st.session_state['phone_code_hash'] = phone_code_hash
                    return True
                except Exception as e:
                    st.error(f"Ошибка при отправке кода: {e}")
                    logger.error(f"Ошибка отправки кода: {e}")
                    if 'session_manager' in st.session_state:
                        del st.session_state['session_manager']
                    return False

            if asyncio.run(start()):
                st.rerun()
    else:
        with st.form(key="code_form"):
            code = st.text_input("Введите код из Telegram", max_chars=10)
            submitted = st.form_submit_button("Подтвердить код")
            if submitted:
                import asyncio
                async def finish():
                    # Используем существующий менеджер из сессии
                    manager = st.session_state.get('session_manager')
                    if not manager:
                        st.error("Ошибка: сессия истекла. Пожалуйста, запросите код заново.")
                        # Очищаем состояние, чтобы пользователь мог начать сначала
                        del st.session_state['phone_code_hash']
                        st.rerun()
                        return

                    try:
                        await manager.finish_auth(code, st.session_state['phone_code_hash'])
                        st.success("Сессия успешно создана. Страница будет перезагружена.")
                        logger.info("Сессия создана.")
                        # Очищаем все временные данные из сессии
                        del st.session_state['phone_code_hash']
                        del st.session_state['session_manager']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при создании сессии: {e}")
                        logger.error(f"Ошибка создания сессии: {e}")
                asyncio.run(finish())
        st.info("Код отправлен на ваш Telegram. Введите его для завершения авторизации.")
# endregion FUNCTION _handle_create_session_button

# region FUNCTION render_auth_menu
# CONTRACT
# Args:
#   - None
# Returns:
#   - None
# Side Effects:
#   - Отображает форму и статус через streamlit
#   - Логирует действия
# Raises:
#   - None
def render_auth_menu() -> None:
    """
    Главная функция-оркестратор: отображает форму авторизации Telegram API и управляет логикой отображения статуса/кнопок.
    """
    st.markdown("### Авторизация")
    st.info("Данные для подключения к Telegram API. Сохраняются в файл .env в корне проекта.")
    user_data = get_user_data()
    _display_auth_form(user_data)
    st.markdown("---")
    _display_session_block(user_data)
# endregion FUNCTION render_auth_menu