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
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Ошибка при сохранении данных: {e}")
        logger.error(f"Ошибка сохранения .env: {e}")
# endregion FUNCTION _handle_form_submission

# region FUNCTION _display_auth_form
# CONTRACT
# Args:
#   - user_data: Optional[UserEnvData] — текущие данные пользователя или None
# Returns:
#   - None
# Side Effects:
#   - Отображает форму через streamlit
#   - При сабмите вызывает _handle_form_submission
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
# endregion FUNCTION _display_auth_form

# region FUNCTION _display_status_and_actions
# CONTRACT
# Args:
#   - user_data: UserEnvData — данные пользователя
# Returns:
#   - None
# Side Effects:
#   - Показывает статус сессии и кнопки через streamlit
#   - Удаляет сессии и данные пользователя при нажатии кнопки
#   - Логирует действия
#   - Перезапускает страницу через st.experimental_rerun
# Raises:
#   - None (ошибки отображаются пользователю и логируются)
def _display_status_and_actions(user_data: UserEnvData) -> None:
    """
    Отображает статус сессии и действия (например, удаление сессии и данных).
    """
    phone_number = user_data.phone_number
    session_exists = SessionManager.session_file_exists(phone_number)

    if session_exists:
        st.success(f"✅ Активная сессия найдена для номера {phone_number}")

    st.markdown("---")
    if st.button("Удалить данные и сессию", key="delete_auth_data", type="primary", help="ВНИМАНИЕ: действие необратимо!"):
        try:
            logger.info(f"Удаление данных и сессии для номера: {phone_number}")
            SessionManager.remove_all_sessions_by_phone(phone_number)
            clear_user_data()
            st.success("Все данные и файлы сессии были удалены.")
            logger.info("Данные и сессия удалены.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Ошибка при удалении данных: {e}")
            logger.error(f"Ошибка удаления данных: {e}")
# endregion FUNCTION _display_status_and_actions

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

    # Функция отображения формы всегда вызывается
    _display_auth_form(user_data)

    # Статус и кнопка удаления отображаются только если данные существуют
    if user_data:
        _display_status_and_actions(user_data)
# endregion FUNCTION render_auth_menu