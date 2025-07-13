"""
Файл: sidebar.py

Назначение:
    Компонент Streamlit для отображения бокового меню.

Функции:
    - render_sidebar_menu(): Отображает меню слева с пунктами 'Авторизация' и 'Парсинг'.

Зависимости:
    - streamlit
"""

# region Импорты
import streamlit as st
# endregion

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