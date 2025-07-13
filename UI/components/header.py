"""
Файл: header.py

Назначение:
    Компонент Streamlit для отображения заголовка приложения.

Функции:
    - render_header(): Отображает заголовок приложения.

Зависимости:
    - streamlit
"""

# region Импорты
import streamlit as st
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