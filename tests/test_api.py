import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


def test_process_success():
    """Тест успешной обработки запроса"""
    with patch('services.processor.TextProcessor.process') as mock_process:
        mock_process.return_value = {
            "result": "Test response",
            "cached": False,
            "processing_time": 0.5
        }
        
        response = client.post(
            "/api/v1/process",
            json={
                "text": "Test text",
                "scenario": "business_letter"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Test response"
        assert data["cached"] == False
        assert "processing_time" in data


def test_process_validation_error():
    """Тест ошибки валидации - пустой текст"""
    response = client.post(
        "/api/v1/process",
        json={
            "text": "",
            "scenario": "business_letter"
        }
    )
    
    # Pydantic возвращает 422 для ошибок валидации
    assert response.status_code == 422


def test_process_long_text():
    """Тест превышения максимальной длины текста"""
    long_text = "a" * 501
    response = client.post(
        "/api/v1/process",
        json={
            "text": long_text,
            "scenario": "business_letter"
        }
    )
    
    # Pydantic возвращает 422 для ошибок валидации
    assert response.status_code == 422


def test_process_invalid_scenario():
    """Тест невалидного сценария"""
    response = client.post(
        "/api/v1/process",
        json={
            "text": "Test text",
            "scenario": "invalid_scenario"
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error


def test_process_llm_error():
    """Тест ошибки LLM сервиса"""
    with patch('services.processor.TextProcessor.process') as mock_process:
        from llm.client import LLMServiceError
        mock_process.side_effect = LLMServiceError("LLM service error")
        
        response = client.post(
            "/api/v1/process",
            json={
                "text": "Test text",
                "scenario": "business_letter"
            }
        )
        
        assert response.status_code == 503
        data = response.json()
        assert "LLM service error" in str(data["detail"])


def test_process_fallback_scenario():
    """Тест fallback-ответа при ошибке LLM"""
    with patch('services.processor.TextProcessor.process') as mock_process:
        from llm.client import LLMServiceError
        # Мокируем, что fallback включен
        with patch('llm.client.Settings') as mock_settings:
            mock_settings.use_fallback = True
            mock_settings.fallback_responses = {
                "business_letter": "Fallback business response",
                "social_post": "Fallback social response",
                "creative": "Fallback creative response"
            }
            mock_process.side_effect = LLMServiceError("LLM service error")
            
            response = client.post(
                "/api/v1/process",
                json={
                    "text": "Test text",
                    "scenario": "social_post"
                }
            )
            
            # При fallback=True сервис должен вернуть 503 с fallback-ответом
            assert response.status_code == 503
            data = response.json()
            assert "detail" in data
            assert data["detail"]["error_type"] == "llm_service_error"


def test_health_check():
    """Тест эндпоинта health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
