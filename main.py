import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from api.routes import router

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Запуск LLM сервиса...")
    logger.info(f"Конфигурация: модель={settings.model_name}, URL={settings.base_url}")
    logger.info(f"Параметры LLM: temperature={settings.temperature}, max_tokens={settings.max_tokens}")
    logger.info(f"Кеш TTL: {settings.cache_ttl} секунд")
    logger.info("Сервис успешно запущен")
    
    yield
    
    logger.info("Завершение работы LLM сервиса...")


# Создание приложения
app = FastAPI(
    title="LLM Processing Service",
    description="Сервис для обработки текста с использованием LLM (GitHub Models)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(router)


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки работоспособности"""
    return {"status": "healthy"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации с переводом на русский язык"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(map(str, error.get("loc", [])))
        message = error.get("msg", "")
        
        # Перевод типов ошибок на русский
        if message == "String should have at least 1 character":
            message = "Строка должна содержать хотя бы 1 символ"
        elif message == "String should have at least 2 characters":
            message = "Строка должна содержать хотя бы 2 символа"
        elif message == "String should have at least 3 characters":
            message = "Строка должна содержать хотя бы 3 символа"
        elif message == "String should have at most 500 characters":
            message = "Строка должна содержать не более 500 символов"
        elif message.startswith("Value error, "):
            # Для ошибок из validator
            message = message.replace("Value error, ", "")
        
        errors.append({
            "type": error.get("type", "validation_error"),
            "loc": error.get("loc", []),
            "msg": message,
            "input": error.get("input", "")
        })
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
