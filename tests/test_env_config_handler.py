"""
Файл: test_env_config_handler.py

Назначение:
    Модульные тесты для src/env_config_handler.py:
    - Проверка чтения, записи и базовой логики работы с .env.

Основные компоненты:

Классы:
    - TestEnvConfigHandler(unittest.TestCase):
        Тесты для функций get_user_data, setup_user_data.

Зависимости:
    - unittest
    - unittest.mock
    - os
    - tempfile
    - src.env_config_handler
"""

# region Импорты
import unittest
from unittest.mock import patch
import os
import tempfile
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from src import env_config_handler
import logging
from config.logger import get_logger
logger = get_logger(__name__)
# endregion

# region Класс тестов
class TestEnvConfigHandler(unittest.TestCase):
    # region FUNCTION test_get_user_data_env
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: None
    # Raises: AssertionError
    def test_get_user_data_env(self):
        logger.info('[START_TEST][test_get_user_data_env]')
        # Проверяем чтение реального .env из корня проекта
        data = env_config_handler.get_user_data()
        logger.info(f'[DATA] {data}')
        self.assertIsInstance(data, dict)
        self.assertIn('api_id', data)
        self.assertIn('api_hash', data)
        logger.info('[END_TEST][test_get_user_data_env]')
    # endregion FUNCTION test_get_user_data_env

    # region FUNCTION test_setup_user_data_update
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: None
    # Raises: AssertionError
    def test_setup_user_data_update(self):
        logger.info('[START_TEST][test_setup_user_data_update]')
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write("API_ID=1\n")
            tf.write("API_HASH=abc\n")
            tf.flush()
            with patch.object(env_config_handler, 'ENV_PATH', tf.name):
                # Логируем исходные данные
                old_data = env_config_handler.get_user_data()
                logger.info(f'[OLD_DATA][Перед изменением] {old_data}')
                env_config_handler.setup_user_data("12345", "hashval")
                # Логируем новые данные после изменений
                new_data = env_config_handler.get_user_data()
                logger.info(f'[NEW_DATA][После изменений] {new_data}')
                # Логируем что именно изменилось
                for k in old_data:
                    if old_data[k] != new_data[k]:
                        logger.info(f'[CHANGE][{k}] {old_data[k]} -> {new_data[k]}')
                self.assertEqual(new_data['api_id'], '12345')
                self.assertEqual(new_data['api_hash'], 'hashval')
        os.unlink(tf.name)
        logger.info('[END_TEST][test_setup_user_data_update]')
    # endregion FUNCTION test_setup_user_data_update

# endregion Класс тестов

# region Точка входа
if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(funcName)s] %(message)s')
    unittest.main()
# endregion 