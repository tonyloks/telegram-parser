"""
Файл: app.py

Назначение:
    Основная логика Streamlit-приложения: сборка интерфейса из компонент.

Зависимости:
    - streamlit
    - UI.components
"""

# region Импорты
import streamlit as st
from UI.components import render_header, render_sidebar_menu, render_auth_menu
# endregion

# region FUNCTION run_app
# CONTRACT
# Args:
#   - Нет
# Returns:
#   - None
# Side Effects:
#   - Отображает UI в браузере через streamlit
# Raises:
#   - Нет
def run_app() -> None:
    """
    Основная функция Streamlit-приложения. Отображает меню и заголовок.
    """
    st.set_page_config(page_title="Telegram Parser", layout="wide")
    render_header()
    menu_choice = render_sidebar_menu()
    if menu_choice == "Авторизация":
        render_auth_menu()
    elif menu_choice == "Парсинг":
        st.write(f"Выбран пункт меню: {menu_choice}")
    else:
        st.write(f"Выбран неизвестный пункт меню: {menu_choice}")
# endregion FUNCTION run_app 