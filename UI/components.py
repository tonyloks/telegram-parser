"""
Файл: components.py

Назначение:
    Визуальные компоненты Streamlit-приложения: заголовок и меню.

Основные компоненты:

Функции:
    - render_header(): Отображает заголовок приложения.
    - render_sidebar_menu(): Отображает меню слева с пунктами 'Настройки' и 'Парсинг'.

Зависимости:
    - streamlit
"""

# region Импорты
import streamlit as st
from handlers.yaml_config_handler import get_config, save_config, AppConfigData
from config.logger import get_logger
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
#   - str: выбранный пункт меню ('Настройки' или 'Парсинг')
# Side Effects:
#   - Отображает меню в сайдбаре, меняет session_state
# Raises:
#   - Нет
def render_sidebar_menu() -> str:
    """
    Отображает вертикальное меню слева и возвращает выбранный пункт.
    """
    import streamlit as st

    menu = ["Настройки", "Парсинг"]
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

# region FUNCTION render_settings_menu
# CONTRACT
# Args:
#   - Нет
# Returns:
#   - str: выбранный пункт ('Параметры парсинга' или 'Авторизация в TG-API')
# Side Effects:
#   - Отображает меню настроек, меняет session_state, сохраняет параметры в config.yaml
# Raises:
#   - Нет
def render_settings_menu() -> str:
    """
    Отображает меню настроек с двумя пунктами и возвращает выбранный.
    Если выбран 'Параметры парсинга' — отображает чекбоксы для параметров из config.yaml.
    """
    logger = get_logger(__name__)
    settings_menu = ["Параметры парсинга", "Авторизация в TG-API"]
    if "settings_menu" not in st.session_state:
        st.session_state["settings_menu"] = settings_menu[0]

    def set_settings_menu(item):
        st.session_state["settings_menu"] = item

    st.markdown("### Настройки")
    for item in settings_menu:
        if st.button(item, key=f"settings_{item}", use_container_width=True):
            set_settings_menu(item)

    selected = st.session_state["settings_menu"]

    if selected == "Параметры парсинга":
        config = get_config() or AppConfigData(parse_user_id=True, parse_user_name=False)
        col1, col2 = st.columns(2)
        with col1:
            parse_user_id = st.checkbox(
                "Парсить user-id",
                value=config.parse_user_id,
                key="parse_user_id_checkbox"
            )
        with col2:
            parse_user_name = st.checkbox(
                "Парсить user-name",
                value=config.parse_user_name,
                key="parse_user_name_checkbox"
            )
        if st.button("Сохранить параметры", key="save_parse_params"):
            logger.info("[START_FUNCTION][render_settings_menu] Сохранение параметров парсинга")
            save_config(AppConfigData(parse_user_id=parse_user_id, parse_user_name=parse_user_name))
            st.success("Параметры сохранены!")
            logger.info("[END_FUNCTION][render_settings_menu] Параметры сохранены")
    return selected
# endregion FUNCTION render_settings_menu 