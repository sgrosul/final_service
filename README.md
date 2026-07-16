# LLM Processing Service

End-to-end сервис для обработки текста с использованием LLM (GitHub Models). Сервис поддерживает несколько сценариев обработки текста: деловые письма, посты для социальных сетей и креативные идеи.

## 📋 Содержание

- [Технологический стек](#Технологический-стек)
- [Описание сценариев](#Описание-сценариев)
- [Установка](#Установка)
- [Запуск](#Запуск)
- [API документация](#API-документация)
- [Примеры использования](#Примеры-использования)
- [Структура проекта](#Структура-проекта)
- [Обработка ошибок](#Обработка-ошибок)
- [Кеширование](#Кеширование)
- [CI/CD](#CICD)
- [Тестирование](#Тестирование)

## 🛠 Технологический стек

- **Python 3.9+**
- **FastAPI** — веб-фреймворк для API
- **Pydantic** — валидация данных и настройки
- **GitHub Models API** — LLM провайдер
- **HTTPX** — асинхронный HTTP-клиент
- **Pytest** — фреймворк для тестирования
- **Flake8** — линтер кода
- **Docker** (опционально)

## 📝 Описание сценариев

Сервис поддерживает три сценария обработки текста:

1. **business_letter** — формирование делового письма
   - Официально-деловой стиль
   - Четкие формулировки
   - Профессиональная структура

2. **social_post** — создание поста для социальных сетей
   - Разговорный стиль
   - Эмоциональное содержание
   - Призывы к действию

3. **creative** — генерация креативных идей
   - Оригинальные решения
   - Нестандартное мышление
   - Вдохновляющий контент

## 📦 Установка

### Требования

- Python 3.9 или выше
- API-ключ от GitHub Models

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/sgrosul/final_service.git>
cd final_service
```

2. Создайте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе шаблона:
```bash
cp .env.example .env
```

## 🚀 Запуск

### Локальный запуск

```bash
python main.py
```

Сервис запустится на `http://127.0.0.1:8000`

### Запуск с помощью uvicorn

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Запуск с Docker (опционально)

Создайте `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
```

Создайте `docker-compose.yml`:
```yaml
version: '3.8'

services:
  llm-service:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
```

Запустите:
```bash
docker-compose up --build
```

## 📚 API документация\n\nПосле запуска сервиса доступна интерактивная документация:

- **Swagger UI**: `http://localhost:8000/docs`

### Эндпоинты

#### POST `/api/v1/process`

Обработка текста с использованием LLM.

**Request body:**
```json
{
  "text": "Текст для обработки",
  "scenario": "business_letter"
}
```

**Response (успех):**
```json
{
  "result": "Сгенерированный текст...",
  "cached": false,
  "processing_time": 2.35
}
```

**Response (ошибка валидации):**
```json
{
  "detail": "Текст не может быть пустым",
  "status_code": 400,
  "error_type": "validation_error"
}
```

**Response (ошибка LLM):**
```json
{
  "detail": "LLM сервис временно недоступен. Попробуйте позже.",
  "status_code": 503,
  "error_type": "llm_service_error"
}
```

#### GET `/health`

Проверка работоспособности сервиса.

**Response:**
```json
{
  "status": "healthy"
}
```

## 💡 Примеры использования

### Пример 1: Деловое письмо

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Нужно написать письмо клиенту с предложением сотрудничества",
    "scenario": "business_letter"
  }'
```

**Response:**
```json
{
  "result": "Уважаемый коллега!\n\nНадеюсь, у Вас всё хорошо. Мы хотели бы предложить Вам сотрудничество в области...",
  "cached": false,
  "processing_time": 3.21
}
```

### Пример 2: Пост для соцсетей

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Анонс запуска нового продукта",
    "scenario": "social_post"
  }'
```

**Response:**
```json
{
  "result": "🚀 Новое время начинается уже сейчас! Наш новый продукт...",
  "cached": false,
  "processing_time": 2.87
}
```

### Пример 3: Креативные идеи

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Идеи для маркетинговой кампании ко Дню всех святых",
    "scenario": "creative"
  }'
```

**Response:**
```json
{
  "result": "💡 Идеи для кампании:\n1. Квест по городу с розыгрышем призов\n2. Коллаборация с местными...",
  "cached": false,
  "processing_time": 2.45
}
```

### Пример 4: Использование кеша

При повторном запросе с тем же текстом и сценарием будет использован кеш:

**Request:**
```bash
# Первый запрос (CACHE MISS)
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Тест", "scenario": "business_letter"}'

# Ответ: "cached": false

# Второй запрос (CACHE HIT)
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Тест", "scenario": "business_letter"}'

# Ответ: "cached": true, processing_time: ~0.001
```

## 📁 Структура проекта

```
final_service/
├── api/                  # API слой (FastAPI роуты)
│   ├── __init__.py
│   └── routes.py         # Эндпоинты API
├── cache/               # Кеширование
│   ├── __init__.py
│   └── cache.py         # InMemoryCache с TTL
├── config/              # Конфигурация
│   ├── __init__.py
│   └── settings.py      # Настройки через переменные окружения
├── llm/                 # LLM модуль
│   ├── __init__.py
│   ├── client.py        # Клиент для GitHub Models API
│   └── prompt_builder.py # Формирование промптов
├── services/            # Бизнес-логика
│   ├── __init__.py
│   └── processor.py     # Обработчик текста
├── tests/               # Тесты
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_cache.py
│   └── test_llm.py
├── .env                 # Переменные окружения (не в репозитории!)
├── .env.example         # Шаблон переменных
├── .gitignore
├── main.py              # Точка входа
├── requirements.txt
├── README.md
└── TESTING.md           # Документация по тестированию
```

## ⚠️ Обработка ошибок

### Ошибки валидации (400/422)

- Пустой текст
- Превышение максимальной длины (500 символов)
- Неверный сценарий

### Ошибки LLM сервиса (503)

- Отсутствует API-ключ
- Неверный API-ключ
- Превышен лимит запросов
- Сервер LLM недоступен
- Таймаут соединения

### Fallback-ответы

При включенном режиме fallback (по умолчанию `USE_FALLBACK=true`) сервис возвращает шаблонное сообщение при недоступности LLM:

```json
{
  "result": "[Сервис временно недоступен. Пожалуйста, попробуйте позже.]\n\nВаше деловое письмо не может быть сгенерировано из-за технических неполадок. Мы работаем над устранением проблемы.",
  "cached": false,
  "processing_time": 0.0,
  "fallback": true
}
```

## 🔒 Кеширование

### Настройки кеша

- **TTL**: 600 секунд (10 минут) по умолчанию
- **Ключ**: хеш от текста + сценарий
- **Хранение**: in-memory (словарь Python)

### Логирование

```
INFO: CACHE MISS для сценария 'business_letter'
INFO: CACHE HIT для сценария 'business_letter'
```

### Управление кешем

Кеш автоматически очищает устаревшие записи. Для полной очистки можно использовать метод `cache.clear()`.

## 🔄 CI/CD

### GitHub Actions

Пайплайн настроен в `.github/workflows/ci.yml` и выполняет:

1. Установку зависимостей
2. Запуск линтера (flake8)
3. Запуск тестов (pytest)
4. Генерацию отчета о покрытии кода (опционально)

### Проверки CI

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Python 3.13
      - Install dependencies
      - Lint with flake8
      - Run tests
      - Run tests with coverage (optional)
```

## 🧪 Тестирование

### Запуск тестов локально

```bash
pytest tests/ -v
```

### Покрытие кода

```bash
pytest tests/ --cov=. --cov-report=xml
```

### Тестовые сценарии

#### API тесты (`test_api.py`)

- ✅ Успешная обработка запроса
- ✅ Ошибка валидации (пустой текст)
- ✅ Ошибка валидации (превышение длины)
- ✅ Ошибка валидации (неверный сценарий)
- ✅ Обработка ошибки LLM
- ✅ Fallback-ответ при ошибке LLM
- ✅ Health check эндпоинт

#### Кеш тесты (`test_cache.py`)

- ✅ Сохранение и извлечение из кеша
- ✅ Cache miss для несуществующего ключа
- ✅ Истечение TTL
- ✅ Разные сценарии для одного текста
- ✅ Статистика кеша
- ✅ Очистка кеша

#### LLM тесты (`test_llm.py`)

- ✅ Успешная генерация ответа
- ✅ Обработка таймаута
- ✅ Обработка ошибки авторизации (401)
- ✅ Обработка серверной ошибки (503)
- ✅ Обработка пустого ответа
- ✅ Обработка отсутствующего API-ключа

---

## 📄 Лицензия

Этот проект создан в образовательных целях как итоговое задание курса "ИИ в инфраструктуре разработки".

---

## 👨‍💻 Автор

Разработано в рамках учебного проекта Нетологии.

---

## 📞 Поддержка

Если у вас возникли вопросы или проблемы с проектом, пожалуйста, создайте issue в репозитории проекта.
