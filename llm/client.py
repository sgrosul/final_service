import logging
import time
from typing import Optional
import httpx
from config.settings import Settings

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Кастомное исключение для ошибок LLM сервиса"""
    pass


class GitHubModelsClient:
    """Клиент для работы с GitHub Models API"""
    
    def __init__(self, settings: Settings):
        self.api_key = settings.openai_api_key
        self.base_url = settings.base_url
        self.model_name = settings.model_name
        self.timeout = settings.timeout
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
        
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Генерация ответа от LLM через GitHub Models API
        
        Args:
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
        
        Returns:
            Сгенерированный текст
        
        Raises:
            LLMServiceError: При ошибках взаимодействия с LLM
        """
        start_time = time.time()
        
        if not self.api_key or len(self.api_key.strip()) == 0:
            logger.error("Отсутствует API ключ GitHub Models")
            raise LLMServiceError(
                "Не удалось получить доступ к LLM сервису. Проверьте учетные данные."
            )
        
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            logger.info(f"Отправка запроса к GitHub Models. Длина промпта: {len(user_prompt)} символов")
            
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
                follow_redirects=True
            )
            
            # Обработка HTTP ошибок
            if response.status_code == 401 or response.status_code == 403:
                logger.error("Ошибка авторизации (401/403)")
                raise LLMServiceError(
                    "Ошибка авторизации в LLM сервисе. Проверьте API ключ."
                )
            elif response.status_code == 429:
                logger.error("Превышен лимит запросов (429)")
                raise LLMServiceError(
                    "Превышен лимит запросов к LLM сервису. Попробуйте позже."
                )
            elif response.status_code == 400:
                logger.error(f"Неверный запрос (400): {response.text}")
                raise LLMServiceError("Неверный формат запроса к LLM сервису.")
            elif response.status_code >= 500:
                logger.error(f"Серверная ошибка LLM: {response.status_code}")
                raise LLMServiceError(
                    "LLM сервис временно недоступен. Попробуйте позже."
                )
            
            response.raise_for_status()
            
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not answer or not answer.strip():
                logger.warning("Получен пустой ответ от модели")
                raise LLMServiceError("Получен пустой ответ от LLM сервиса.")
            
            elapsed = time.time() - start_time
            logger.info(f"Ответ успешно получен. Длина: {len(answer)} символов, время: {elapsed:.2f}с")
            
            return answer.strip()
            
        except httpx.TimeoutException:
            logger.error(f"Таймаут при вызове API (таймаут: {self.timeout}с)")
            raise LLMServiceError(
                f"Превышено время ожидания ответа от LLM сервиса ({self.timeout}с)."
            )
        except httpx.ConnectError as e:
            logger.error(f"Ошибка подключения: {str(e)}")
            raise LLMServiceError(
                "Не удалось подключиться к LLM сервису. Проверьте соединение."
            )
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети: {str(e)}")
            raise LLMServiceError("Ошибка сети при обращении к LLM сервису.")
        except ValueError as e:
            logger.error(f"Ошибка разбора JSON ответа: {str(e)}")
            raise LLMServiceError("Некорректный ответ от LLM сервиса.")
        except LLMServiceError:
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {str(e)}")
            raise LLMServiceError("Произошла непредвиденная ошибка при обращении к LLM.")
