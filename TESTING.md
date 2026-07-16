# 🧪 Тестирование LLM Processing Service

Документация по тестированию сервиса обработки текста с использованием LLM.

## 🚀 Запуск тестов

### Локальный запуск

```bash
# Запуск всех тестов с подробным выводом
pytest tests/ -v

# Запуск с покрытием кода
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Запуск конкретного файла
pytest tests/test_api.py -v
pytest tests/test_cache.py -v
pytest tests/test_llm.py -v

# Запуск конкретного теста
pytest tests/test_api.py::test_process_success -v
```

### Запуск в CI/CD

Пайплайн настраивается в `.github/workflows/ci.yml` и автоматически запускает:
```bash
pytest tests/ -v
```

---

## 🧩 Тестовые сценарии

### API Тесты (`tests/test_api.py`)

| Тест | Описание | Ожидаемый результат |
|------|----------|---------------------|
| `test_process_success` | Успешная обработка запроса | `response.status_code == 200` |
| `test_process_validation_error` | Ошибка валидации (пустой текст) | `response.status_code == 422` |
| `test_process_long_text` | Превышение максимальной длины (500 символов) | `response.status_code == 422` |
| `test_process_invalid_scenario` | Неверный сценарий | `response.status_code == 422` |
| `test_process_llm_error` | Ошибка LLM сервиса | `response.status_code == 503` |
| `test_process_fallback_scenario` | Fallback-ответ при ошибке LLM | `response.status_code == 503` |
| `test_health_check` | Health check эндпоинт | `response.status_code == 200`, `{\"status\": \"healthy\"}` |

### Cache Тесты (`tests/test_cache.py`)

| Тест | Описание | Ожидаемый результат |
|------|----------|---------------------|
| `test_cache_set_get` | Сохранение и извлечение из кеша | `result == \"test_value\"` |
| `test_cache_miss` | Cache miss для несуществующего ключа | `result is None` |
| `test_cache_ttl` | Истечение TTL | `result is None` после истечения |
| `test_cache_different_scenarios` | Разные сценарии для одного текста | `result1 != result2` |
| `test_cache_stats` | Статистика кеша | `stats[\"total_entries\"] == 2` |
| `test_cache_clear` | Очистка кеша | `result is None` после `cache.clear()` |

### LLM Тесты (`tests/test_llm.py`)

| Тест | Описание | Ожидаемый результат |
|------|----------|---------------------|
| `test_generate_response_success` | Успешная генерация ответа | `result == \"Test response\"` |
| `test_generate_response_timeout` | Обработка таймаута | Исключение содержит \"Превышено время ожидания\" |
| `test_generate_response_unauthorized` | Обработка ошибки авторизации (401) | Исключение содержит \"Ошибка авторизации\" |
| `test_generate_response_server_error` | Обработка серверной ошибки (503) | Исключение содержит \"LLM сервис временно недоступен\" |
| `test_generate_response_empty_response` | Обработка пустого ответа | Исключение содержит \"Получен пустой ответ\" |
| `test_generate_response_missing_api_key` | Обработка отсутствующего API ключа | Исключение содержит \"Не удалось получить доступ\" |

---

## 🔍 Ручное тестирование API

### Установка зависимостей и запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
# Отредактируйте .env, добавив ваш OPENAI_API_KEY

# Запуск сервиса
python main.py
# или
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Тестовые запросы

#### 1. Успешный запрос (cache miss → cache hit)

```bash
# Первый запрос (CACHE MISS)
curl -X POST http://127.0.0.1:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Тест кеширования", "scenario": "business_letter"}'

# Второй запрос (CACHE HIT)
curl -X POST http://127.0.0.1:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Тест кеширования", "scenario": "business_letter"}'
```

**Ожидаемый результат**: первый запрос `cached: false`, второй `cached: true`

---

#### 2. Ошибка валидации (пустой текст)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "", "scenario": "business_letter"}'
```

**Ожидаемый результат**: `422 Unprocessable Entity`

---

#### 3. Ошибка валидации (превышение длины)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "a" * 501, "scenario": "social_post"}'
```

**Ожидаемый результат**: `422 Unprocessable Entity`

---

#### 4. Fallback-ответ (отключить API ключ)

1. Отключите API ключ в `.env` (оставьте пустым)
2. Запустите сервис
3. Отправьте запрос:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "scenario": "business_letter"}'
```

**Ожидаемый результат**: `503 Service Unavailable` с fallback-ответом

---

#### 5. Health check

```bash
curl http://127.0.0.1:8000/health
```

**Ожидаемый результат**: `{\"status\": \"healthy\"}`

---

## 📊 Логирование

### Уровни логирования

- **INFO**: Успешные запросы, cache hit/miss, старт/стоп сервиса
- **WARNING**: Валидационные ошибки
- **ERROR**: Ошибки LLM, сетевые ошибки, внутренние ошибки

### Просмотр логов

```bash
# Запустите сервис с логированием
python main.py

# Или с debug уровнем
LOG_LEVEL=DEBUG python main.py
```

---

## 🐛 Отладка

### Тесты не запускаются

**Проблема**: `ModuleNotFoundError`

**Решение**:
```bash
# Активируйте виртуальное окружение
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Переустановите зависимости
pip install -r requirements.txt
```

---

### Тесты падают с ошибкой API

**Проблема**: `LLMServiceError: Не удалось получить доступ к LLM сервису`

**Решение**:
1. Проверьте, что `OPENAI_API_KEY` установлен в `.env`
2. Проверьте, что ключ валиден
3. Убедитесь, что у вас есть доступ к GitHub Models API

---

### Кеширование не работает

**Проблема**: CACHE MISS для повторных запросов

**Решение**:
1. Проверьте логи: `CACHE MISS` и `CACHE HIT` должны логироваться
2. Убедитесь, что один и тот же текст и сценарий используются
3. Проверьте TTL: если TTL истек, кеш очищается автоматически

---

## ✅ Результаты тестирования

### Автоматические тесты
- [x] Все 19 тестов проходят успешно (`pytest tests/ -v`)
- [x] Покрытие кода > 80% (`pytest tests/ --cov=.`) — **85%**
- [x] Линтер flake8 не выдает критических ошибок (`flake8 . --select=E9,F63,F7,F82`)

### Ручное тестирование
- [x] Сервис запускается одной командой
- [x] Успешный запрос возвращает 200 OK
- [x] Ошибки валидации возвращают 422
- [x] Ошибки LLM возвращают 503
- [x] Fallback-ответ возвращается при недоступности LLM
- [x] Кеширование работает (cache hit/miss логируется)
- [x] Health check возвращает 200 OK

---

