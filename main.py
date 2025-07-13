"""
Файл: main.py

Назначение:
    Точка входа для Streamlit-приложения (импортирует и запускает UI/app.py).

Зависимости:
    - streamlit
    - UI.app
"""

# region Импорты
from UI.app import run_app
# endregion

# region Точка входа
if __name__ == "__main__":
    run_app()
# endregion 