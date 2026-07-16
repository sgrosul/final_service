from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GitHub Models settings
    openai_api_key: str
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
