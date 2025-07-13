"""
Файл: app.py

Назначение:
    Streamlit-приложение для управления настройками и запуском парсинга.

Основные компоненты:

Функции:
    - main(): Точка входа, отображает интерфейс с вкладками.

Зависимости:
    - streamlit
"""

# region Импорты
import streamlit as st
from UI.components import render_header, render_sidebar_menu
# endregion

# region FUNCTION main
# CONTRACT
# Args:
#   - Нет
# Returns:
#   - None
# Side Effects:
#   - Отображает UI в браузере через streamlit
# Raises:
#   - Нет

def main() -> None:
    """
    Точка входа для Streamlit-приложения. Отображает меню и заголовок.
    """
    st.set_page_config(page_title="Telegram Parser", layout="wide")
    render_header()
    menu_choice = render_sidebar_menu()
    if menu_choice == "Настройки":
        from UI.components import render_settings_menu
        settings_choice = render_settings_menu()
        st.write(f"Выбран раздел настроек: {settings_choice}")
    else:
        st.write(f"Выбран пункт меню: {menu_choice}")
# endregion FUNCTION main

# region Точка входа
if __name__ == "__main__":
    main()
# endregion 