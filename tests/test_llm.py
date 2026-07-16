import pytest
from unittest.mock import Mock, patch
import re
from llm.client import GitHubModelsClient, LLMServiceError
from config.settings import Settings


@pytest.fixture
def mock_settings():
    """Фикстура для мокирования настроек"""
    mock = Mock(spec=Settings)
    mock.openai_api_key = "test_api_key"
    mock.base_url = "https://models.github.ai/inference"
    mock.model_name = "openai/gpt-4o"
    mock.timeout = 30
    mock.temperature = 0.7
    mock.max_tokens = 500
    return mock


def test_generate_response_success(mock_settings):
    """Тест успешной генерации ответа"""
    with patch('httpx.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        client = GitHubModelsClient(mock_settings)
        result = client.generate_response("system", "user")
        assert result == "Test response"


def test_generate_response_timeout(mock_settings):
    """Тест обработки таймаута"""
    with patch('httpx.post') as mock_post:
        from httpx import TimeoutException
        mock_post.side_effect = TimeoutException("Timeout")
        
        client = GitHubModelsClient(mock_settings)
        with pytest.raises(LLMServiceError) as exc_info:
            client.generate_response("system", "user")
        assert "Превышено время ожидания" in str(exc_info.value)


def test_generate_response_unauthorized(mock_settings):
    """Тест обработки ошибки авторизации"""
    with patch('httpx.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        client = GitHubModelsClient(mock_settings)
        with pytest.raises(LLMServiceError) as exc_info:
            client.generate_response("system", "user")
        assert "Ошибка авторизации" in str(exc_info.value) or "Error" in str(exc_info.value)


def test_generate_response_server_error(mock_settings):
    """Тест обработки серверной ошибки"""
    with patch('httpx.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.text = "Service Unavailable"
        mock_post.return_value = mock_response
        
        client = GitHubModelsClient(mock_settings)
        with pytest.raises(LLMServiceError) as exc_info:
            client.generate_response("system", "user")
        assert "LLM сервис временно недоступен" in str(exc_info.value)


def test_generate_response_empty_response(mock_settings):
    """Тест обработки пустого ответа"""
    with patch('httpx.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": ""}}]
        }
        mock_post.return_value = mock_response
        
        client = GitHubModelsClient(mock_settings)
        with pytest.raises(LLMServiceError) as exc_info:
            client.generate_response("system", "user")
        assert re.search(r"Получен пустой ответ", str(exc_info.value), re.IGNORECASE) is not None


def test_generate_response_missing_api_key(mock_settings):
    """Тест обработки отсутствующего API ключа"""
    mock_settings.openai_api_key = ""
    
    client = GitHubModelsClient(mock_settings)
    with pytest.raises(LLMServiceError) as exc_info:
        client.generate_response("system", "user")
    assert re.search(r"Не удалось получить доступ", str(exc_info.value), re.IGNORECASE) is not None
