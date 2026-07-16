import time
import logging
from typing import Dict, Any
from llm.client import GitHubModelsClient, LLMServiceError
from llm.prompt_builder import build_prompt
from cache.cache import cache
from config.settings import settings

logger = logging.getLogger(__name__)


# Шаблонные fallback-ответы для разных сценариев
FALLBACK_RESPONSES = {
    "business_letter": (
        "[Сервис временно недоступен. Пожалуйста, попробуйте позже.]\n\n"
        "Ваше деловое письмо не может быть сгенерировано из-за технических неполадок. "
        "Мы работаем над устранением проблемы."
    ),
    "social_post": (
        "[Сервис временно недоступен. Пожалуйста, попробуйте позже.]\n\n"
        "Ваш пост для социальных сетей не может быть сгенерирован из-за технических неполадок. "
        "Мы работаем над устранением проблемы."
    ),
    "creative": (
        "[Сервис временно недоступен. Пожалуйста, попробуйте позже.]\n\n"
        "Идеи не могут быть сгенерированы из-за технических неполадок. "
        "Мы работаем над устранением проблемы."
    )
}


class TextProcessor:
    """Обработчик текста с использованием LLM"""
    
    def __init__(self):
        self.llm_client = GitHubModelsClient(settings)
        self.max_text_length = 500
        self.use_fallback = settings.use_fallback if hasattr(settings, 'use_fallback') else True
    
    def process(self, text: str, scenario: str) -> Dict[str, Any]:
        """
        Обработка текста с использованием LLM
        
        Args:
            text: Входной текст
            scenario: Сценарий обработки
        
        Returns:
            Dict с результатом и метаданными
        
        Raises:
            ValueError: При невалидных входных данных
            LLMServiceError: При ошибках LLM (если fallback отключен)
        """
        start_time = time.time()
        
        # 1. Валидация входных данных
        if not text or not text.strip():
            logger.error("Получен пустой текст")
            raise ValueError("Текст не может быть пустым")
        
        if len(text) > self.max_text_length:
            logger.error(f"Превышена максимальная длина текста: {len(text)} > {self.max_text_length}")
            raise ValueError(
                f"Текст превышает максимальную длину в {self.max_text_length} символов"
            )
        
        text = text.strip()
        
        # 2. Проверка кеша
        cached_result = cache.get(text, scenario)
        if cached_result is not None:
            elapsed = time.time() - start_time
            logger.info(f"CACHE HIT для сценария '{scenario}'")
            return {
                "result": cached_result,
                "cached": True,
                "processing_time": elapsed
            }
        
        logger.info(f"CACHE MISS для сценария '{scenario}'")
        
        # 3. Формирование промпта
        prompts = build_prompt(text, scenario)
        logger.info(f"Сформирован промпт для сценария '{scenario}'")
        
        # 4. Запрос к LLM
        try:
            response = self.llm_client.generate_response(
                prompts["system"],
                prompts["user"]
            )
        except LLMServiceError as e:
            logger.error(f"Ошибка LLM: {str(e)}")
            
            # Fallback-ответ при недоступности LLM
            if self.use_fallback:
                fallback_response = FALLBACK_RESPONSES.get(scenario, FALLBACK_RESPONSES["business_letter"])
                logger.info(f"Возврат fallback-ответа для сценария '{scenario}'")
                return {
                    "result": fallback_response,
                    "cached": False,
                    "processing_time": 0.0,
                    "fallback": True
                }
            else:
                raise
        
        # 5. Пост-обработка ответа
        processed_response = response.strip()
        logger.info(f"Пост-обработка завершена. Длина ответа: {len(processed_response)} символов")
        
        # 6. Сохранение в кеш
        cache.set(text, scenario, processed_response)
        logger.info("Результат сохранен в кеш")
        
        elapsed = time.time() - start_time
        return {
            "result": processed_response,
            "cached": False,
            "processing_time": elapsed
        }
