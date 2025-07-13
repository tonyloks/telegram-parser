"""
Файл: test_yaml_config_handler.py

Назначение:
    Модульные тесты для src/yaml_config_handler.py:
    - Проверка чтения, записи и базовой логики работы с config.yaml.

Основные компоненты:

Классы:
    - TestYamlConfigHandler(unittest.TestCase):
        Тесты для функций get_config, save_config.

Зависимости:
    - unittest
    - unittest.mock
    - yaml
    - src.yaml_config_handler
"""

# region Импорты
import unittest
from unittest.mock import patch, mock_open
import yaml
from handlers import yaml_config_handler
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
from config.logger import get_logger
logger = get_logger(__name__)
# endregion

# region Класс тестов
class TestYamlConfigHandler(unittest.TestCase):
    # region FUNCTION test_get_config_file_not_exists
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: None
    # Raises: AssertionError
    def test_get_config_file_not_exists(self):
        logger.info('[START_TEST][test_get_config_file_not_exists]')
        with patch('os.path.exists', return_value=False):
            self.assertEqual(yaml_config_handler.get_config(), {})
        logger.info('[END_TEST][test_get_config_file_not_exists]')
    # endregion FUNCTION test_get_config_file_not_exists

    # region FUNCTION test_get_config_valid_yaml
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: None
    # Raises: AssertionError
    def test_get_config_valid_yaml(self):
        logger.info('[START_TEST][test_get_config_valid_yaml]')
        fake_yaml = 'api_id: 123\napi_hash: "abc"\nparse_user_id: true\nparse_user_name: false\n'.replace('\\n', '\n')
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=fake_yaml)):
            result = yaml_config_handler.get_config()
            self.assertEqual(result['api_id'], 123)
            self.assertEqual(result['api_hash'], 'abc')
            self.assertTrue(result['parse_user_id'])
            self.assertFalse(result['parse_user_name'])
        logger.info('[END_TEST][test_get_config_valid_yaml]')
    # endregion FUNCTION test_get_config_valid_yaml

    # region FUNCTION test_save_config
    # CONTRACT
    # Args: None
    # Returns: None
    # Side Effects: None
    # Raises: AssertionError
    def test_save_config(self):
        logger.info('[START_TEST][test_save_config]')
        data = {'api_id': 1, 'api_hash': 'x', 'parse_user_id': True, 'parse_user_name': False}
        m = mock_open()
        with patch('builtins.open', m):
            yaml_config_handler.save_config(data)
            m.assert_called_once_with(yaml_config_handler.CONFIG_PATH, 'w', encoding='utf-8')
            handle = m()
            written = ''.join(call.args[0] for call in handle.write.call_args_list)
            loaded = yaml.safe_load(written)
            self.assertEqual(loaded, data)
        logger.info('[END_TEST][test_save_config]')
    # endregion FUNCTION test_save_config
# endregion Класс тестов

# region Точка входа
if __name__ == "__main__":
    unittest.main()
# endregion 