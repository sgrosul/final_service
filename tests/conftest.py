import os
import pytest
from unittest.mock import patch

# Устанавливаем переменные окружения ДО импорта любых модулей приложения
os.environ["OPENAI_API_KEY"] = "test-dummy-key-for-pytest"
os.environ["USE_FALLBACK"] = "true"  # Если у вас есть такая настройка

# Опционально: можно полностью замокать экземпляр settings для всех тестов,
# чтобы они не зависели от реального файла .env
@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with patch("config.settings.settings.openai_api_key", "test-dummy-key"):
        yield