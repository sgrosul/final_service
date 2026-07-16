from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GitHub Models settings
    # Делаем опциональным (None по умолчанию), чтобы тесты и CI не падали 
    # с ValidationError, если переменная окружения не задана
    openai_api_key: Optional[str] = None
    base_url: str = "https://models.github.ai/inference"
    model_name: str = "openai/gpt-4o"
    
    # LLM parameters
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30
    
    # Cache settings
    cache_ttl: int = 600
    
    # Logging
    log_level: str = "INFO"
    
    # Fallback settings
    use_fallback: bool = True
    
    # Настройки Pydantic V2 (замена устаревшему class Config)
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорируем неизвестные переменные окружения, чтобы не было ошибок
    )


# Глобальный экземпляр настроек
settings = Settings()