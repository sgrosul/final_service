from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import Literal
import logging
from services.processor import TextProcessor
from llm.client import LLMServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["process"])
processor = TextProcessor()


class ProcessRequest(BaseModel):
    """Модель запроса на обработку текста"""
    text: str = Field(..., description="Текст для обработки", min_length=1)
    scenario: Literal["business_letter", "social_post", "creative"] = Field(
        ...,
        description="Сценарий обработки"
    )
    
    @validator('text')
    def validate_text_length(cls, v):
        if len(v) > 500:
            raise ValueError(f"Текст не может превышать 500 символов (получено {len(v)})")
        return v


class ProcessResponse(BaseModel):
    """Модель ответа на обработку текста"""
    result: str = Field(..., description="Сгенерированный результат")
    cached: bool = Field(..., description="Был ли использован кеш")
    processing_time: float = Field(..., description="Время обработки в секундах")


class ErrorResponse(BaseModel):
    """Модель ошибки"""
    detail: str = Field(..., description="Описание ошибки")
    status_code: int = Field(..., description="HTTP статус-код")
    error_type: str = Field(..., description="Тип ошибки")


@router.post(
    "/process",
    response_model=ProcessResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        503: {"model": ErrorResponse, "description": "Ошибка LLM сервиса"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def process_text(request: Request, req_data: ProcessRequest):
    """
    Обработка текста с использованием LLM
    
    Принимает текст и сценарий, возвращает сгенерированный результат
    с информацией о кешировании и времени обработки.
    """
    # Логирование запроса
    logger.info(f"POST /api/v1/process - scenario: {req_data.scenario}, text_length: {len(req_data.text)}")
    
    try:
        # Обработка текста
        result = processor.process(req_data.text, req_data.scenario)
        logger.info(f"Успешная обработка: cached={result['cached']}, time={result['processing_time']:.3f}s")
        return result
        
    except ValueError as e:
        # Ошибка валидации
        logger.warning(f"Ошибка валидации: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "detail": str(e),
                "status_code": 400,
                "error_type": "validation_error"
            }
        )
    except LLMServiceError as e:
        # Ошибка LLM сервиса
        logger.error(f"Ошибка LLM: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "detail": str(e),
                "status_code": 503,
                "error_type": "llm_service_error"
            }
        )
    except Exception as e:
        # Непредвиденная ошибка
        logger.error(f"Неожиданная ошибка: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "detail": "Внутренняя ошибка сервера",
                "status_code": 500,
                "error_type": "internal_error"
            }
        )
