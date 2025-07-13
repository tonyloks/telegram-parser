"""
Файл: components.py

Назначение:
    Визуальные компоненты Streamlit-приложения: заголовок, меню и форма авторизации Telegram API.

Основные компоненты:

Функции:
    - render_header(): Отображает заголовок приложения.
    - render_sidebar_menu(): Отображает меню слева с пунктами 'Авторизация' и 'Парсинг'.
    - render_auth_menu(): Отображает форму авторизации (API_ID, API_HASH, PHONE_NUMBER) с автозаполнением из .env.

Зависимости:
    - streamlit
    - handlers.env_config_handler (get_user_data, setup_user_data, UserEnvData)
"""

# region Импорты
import streamlit as st
from handlers.env_config_handler import get_user_data, setup_user_data, UserEnvData
from config.logger import get_logger
from modules.session_manager import SessionManager
# endregion

# region FUNCTION render_header
# CONTRACT
# Args:
#   - Нет
# Returns:
#   - None
# Side Effects:
#   - Отображает заголовок в UI
# Raises:
#   - Нет
def render_header() -> None:
    """
    Отображает заголовок приложения.
    """
    st.title("Приложение для выгрузки чатов")
# endregion FUNCTION render_header

# region FUNCTION render_sidebar_menu
# CONTRACT
# Args:
#   - Нет
# Returns:
#   - str: выбранный пункт меню ('Авторизация' или 'Парсинг')
# Side Effects:
#   - Отображает меню в сайдбаре, меняет session_state
# Raises:
#   - Нет
def render_sidebar_menu() -> str:
    """
    Отображает вертикальное меню слева и возвращает выбранный пункт.
    """
    menu = ["Авторизация", "Парсинг"]
    if "menu" not in st.session_state:
        st.session_state["menu"] = menu[0]

    def set_menu(item):
        st.session_state["menu"] = item

    st.sidebar.markdown("## Меню")
    for item in menu:
        if st.sidebar.button(item, key=f"menu_{item}", use_container_width=True):
            set_menu(item)
    return st.session_state["menu"]
# endregion FUNCTION render_sidebar_menu

# region FUNCTION render_auth_menu
# CONTRACT
# Args:
#   - Нет
# Returns:
#   - None
# Side Effects:
#   - Отображает форму авторизации, сохраняет данные в .env
# Raises:
#   - Нет
def render_auth_menu() -> None:
    """
    Отображает форму авторизации Telegram API (API_ID, API_HASH, PHONE_NUMBER) с автозаполнением из .env.
    При сохранении вызывает setup_user_data.
    """
    logger = get_logger(__name__)
    st.markdown("### Авторизация")
    st.info("Данные подгружаются и сохраняются в файл .env в директории проекта.")
    user_data = get_user_data()
    # Проверка сессии через статический метод
    session_status = None
    if user_data:
        if SessionManager.session_file_exists(user_data.phone_number):
            session_status = "Сессия Telegram: найдена"
        else:
            session_status = "Сессия Telegram: не найдена"
        st.info(session_status)
    api_id = st.text_input("API_ID", value=user_data.api_id if user_data else "", key="api_id_input", type="password")
    api_hash = st.text_input("API_HASH", value=user_data.api_hash if user_data else "", key="api_hash_input", type="password")
    phone_number = st.text_input("PHONE_NUMBER", value=user_data.phone_number if user_data else "", key="phone_number_input")
    if st.button("Сохранить", key="save_auth_params"):
        logger.info("[START_FUNCTION][render_auth_menu] Сохранение данных авторизации")
        setup_user_data(UserEnvData(api_id=api_id, api_hash=api_hash, phone_number=phone_number))
        st.success("Параметры авторизации сохранены!")
        logger.info("[END_FUNCTION][render_auth_menu] Данные авторизации сохранены")
# endregion FUNCTION render_auth_menu

# region Удалённая функция render_settings_menu
# endregion 