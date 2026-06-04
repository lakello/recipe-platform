# Backend

Backend Recipe Platform — серверная часть платформы рецептов и планирования питания.

Сервис предоставляет REST API для web, Android и desktop-клиентов, отвечает за бизнес-логику, авторизацию, работу с рецептами, пользователями, комментариями, планом питания, списками покупок, модерацией и интеграциями с внешними сервисами.

## Назначение директории

В директории `backend/` находится код backend-приложения:

- FastAPI-приложение;
- бизнес-модули;
- модели базы данных;
- миграции Alembic;
- фоновые задачи Celery;
- API endpoints;
- тесты;
- Dockerfile для сборки backend image;
- конфигурация зависимостей Python.

## Технологический стек

Планируемый стек backend:

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery
- OpenSearch
- JWT
- OAuth Google
- OAuth Yandex
- Pytest
- Ruff
- Mypy
- Docker

## Ответственность backend

Backend отвечает за:

- регистрацию и авторизацию пользователей;
- email/password login;
- Google OAuth;
- Яндекс OAuth;
- выпуск JWT access token;
- refresh token rotation;
- управление пользователями и профилями;
- роли и права доступа;
- CRUD рецептов;
- загрузку фотографий через Object Storage;
- выдачу pre-signed URL;
- категории рецептов;
- ингредиенты;
- поиск рецептов;
- комментарии;
- лайки;
- избранное;
- подписки;
- недельный план питания;
- автоматическое формирование списка покупок;
- уведомления;
- жалобы на контент;
- модерацию;
- административные функции;
- аудит действий;
- health checks для Docker и Kubernetes;
- метрики и трассировку.

## Предполагаемая структура

```text

backend/

app/

api/

v1/

endpoints/

router.py

core/

config.py

security.py

logging.py

db/

session.py

base.py

models/

schemas/

services/

repositories/

tasks/

integrations/

utils/

main.py

alembic/

versions/

tests/

unit/

integration/

Dockerfile

pyproject.toml

alembic.ini

README.md
```

## Основные модули

### `app/api/`

HTTP API слой.

Содержит роутеры и endpoints:

- `/auth`
- `/users`
- `/profiles`
- `/recipes`
- `/categories`
- `/ingredients`
- `/comments`
- `/likes`
- `/favorites`
- `/follows`
- `/meal-plans`
- `/shopping-lists`
- `/admin`
- `/moderation`
- `/notifications`
- `/uploads`
- `/search`

### `app/core/`

Общая конфигурация приложения:

- переменные окружения;
- security-настройки;
- JWT;
- CORS;
- logging;
- OpenTelemetry;
- rate limiting;
- настройки приложения.

### `app/db/`

Работа с базой данных:

- подключение к PostgreSQL;
- SQLAlchemy session;
- base model;
- metadata для Alembic.

### `app/models/`

SQLAlchemy-модели.

Основные сущности:

- users;
- user_oauth_accounts;
- refresh_tokens;
- roles;
- user_roles;
- profiles;
- recipes;
- recipe_steps;
- ingredients;
- recipe_ingredients;
- categories;
- recipe_photos;
- comments;
- likes;
- favorites;
- follows;
- meal_plans;
- meal_plan_items;
- shopping_lists;
- shopping_list_items;
- notifications;
- reports;
- moderation_actions;
- audit_logs.

### `app/schemas/`

Pydantic-схемы:

- request schemas;
- response schemas;
- DTO;
- validation rules.

### `app/services/`

Бизнес-логика приложения.

Примеры сервисов:

- `AuthService`;
- `UserService`;
- `RecipeService`;
- `UploadService`;
- `SearchService`;
- `MealPlanService`;
- `ShoppingListService`;
- `ModerationService`;
- `NotificationService`.

### `app/repositories/`

Слой доступа к данным.

Репозитории инкапсулируют SQL-запросы и работу с моделями.

### `app/tasks/`

Фоновые задачи Celery:

- отправка email;
- генерация thumbnails;
- обработка изображений;
- пересчёт списков покупок;
- отправка уведомлений;
- синхронизация поискового индекса;
- периодическая очистка истёкших токенов.

### `app/integrations/`

Интеграции с внешними системами:

- Yandex Object Storage;
- Google OAuth;
- Yandex OAuth;
- SMTP;
- OpenSearch;
- Redis.

## API документация

После запуска backend OpenAPI-документация доступна по адресам:

```
/api/docs
/api/openapi.json
```

Swagger UI:

```
/api/docs
```

OpenAPI JSON:

```
/api/openapi.json
```

## Основные API endpoints

### Auth

``` http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/google/login
GET  /api/auth/google/callback
GET  /api/auth/yandex/login
GET  /api/auth/yandex/callback
```

Recipes

``` http
GET    /api/recipes
POST   /api/recipes
GET    /api/recipes/{id}
PATCH  /api/recipes/{id}
DELETE /api/recipes/{id}
POST   /api/recipes/{id}/like
DELETE /api/recipes/{id}/like
POST   /api/recipes/{id}/comments
```

Meal plans

``` http
GET    /api/meal-plans/week
POST   /api/meal-plans/items
PATCH  /api/meal-plans/items/{id}
DELETE /api/meal-plans/items/{id}
POST   /api/meal-plans/copy-next-week
```

Shopping lists

``` http
GET   /api/shopping-lists/current
POST  /api/shopping-lists/recalculate
PATCH /api/shopping-lists/items/{id}
```

## Переменные окружения

Пример переменных окружения:

``` env
APP_ENV=local
APP_NAME=recipe-platform-backend
APP_DEBUG=true

API_PREFIX=/api

DATABASE_URL=postgresql+asyncpg://recipe:recipe@postgres:5432/recipe
REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=change-me
## JWT_ALGORITHM=HS256
# JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
# JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

S3_ENDPOINT_URL=http://minio:9000
S3_BUCKET_NAME=recipe-platform-local
S3_ACCESS_KEY_ID=minio
S3_SECRET_ACCESS_KEY=minio-password

OPENSEARCH_URL=http://opensearch:9200

SMTP_HOST=mailhog
## SMTP_PORT=1025
## SMTP_USER=
## SMTP_PASSWORD=
SMTP_FROM=no-reply@recipe-platform.local

# GOOGLE_OAUTH_CLIENT_ID=
# GOOGLE_OAUTH_CLIENT_SECRET=

# YANDEX_OAUTH_CLIENT_ID=
# YANDEX_OAUTH_CLIENT_SECRET=
```

Значения выше предназначены только как пример. Реальные секреты нельзя хранить в Git.

## Локальный запуск

Рекомендуемый способ локального запуска всего проекта — из корня репозитория через Docker Compose:

```
docker compose up -d
```

Запуск только backend-зависимостей, если такой compose-профиль будет добавлен:

```
docker compose --profile backend up -d
```

## Запуск приложения локально без Docker

Установить зависимости:

``` bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -e ".[dev]"
```

Запустить backend:

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу:

```
http://localhost:8000
```

Документация:

```
http://localhost:8000/api/docs
```

## Миграции базы данных

Для миграций используется Alembic.

Создать новую миграцию:

```
alembic revision --autogenerate -m "create users table"
```

Применить миграции:

```
alembic upgrade head
```

Откатить последнюю миграцию:

```
alembic downgrade -1
```

Посмотреть текущую ревизию:

```
alembic current
```

## Тесты

Для тестирования используется Pytest.

Запуск всех тестов:

```
pytest
```

Запуск unit-тестов:

```
pytest tests/unit
```

Запуск integration-тестов:

```
pytest tests/integration
```

Запуск с отчётом покрытия:

```
pytest --cov=app --cov-report=term-missing
```

## Линтинг и форматирование

Планируемые инструменты:

- Ruff;
- Mypy;
- Pytest.

Проверка Ruff:

```
ruff check .
```

Форматирование Ruff:

```
ruff format .
```

Проверка типов:

```
mypy app
```

## Docker

Backend собирается в отдельный Docker image.

Пример сборки:

```
docker build -t recipe-backend:local .
```

Пример запуска:

```
docker run --rm -p 8000:8000 --env-file .env recipe-backend:local
```

В production image должны соблюдаться требования:

- multi-stage build;
- non-root user;
- минимальный base image;
- отсутствие секретов внутри image;
- использование `.dockerignore`;
- pinned dependencies;
- healthcheck endpoint;
- корректная обработка SIGTERM.

## Health checks

Backend должен предоставлять endpoints для проверки состояния:

``` http
GET /health
GET /ready
```

### `/health`

Проверяет, что приложение запущено.

### `/ready`

Проверяет готовность принимать трафик:

- соединение с PostgreSQL;
- соединение с Redis;
- доступность критичных зависимостей.

Эти endpoints используются:

- Docker;
- Kubernetes livenessProbe;
- Kubernetes readinessProbe;
- мониторингом.

## Observability

Backend должен поддерживать:

- JSON-логи;
- request ID;
- trace ID;
- user ID, если применимо;
- структурированные ошибки;
- Prometheus metrics;
- OpenTelemetry tracing.

### Логи

Логи должны быть пригодны для сбора в Loki.

Пример полей:

``` json
{

"timestamp": "2025-01-01T12:00:00Z",

"level": "INFO",

"service": "backend",

"request_id": "req-123",

"trace_id": "trace-123",

"user_id": "user-123",

"method": "GET",

"path": "/api/recipes",

"status_code": 200,

"duration_ms": 45

}
```

### Метрики

Примеры метрик:

- request rate;
- error rate;
- latency;
- active DB connections;
- Redis errors;
- Celery queue length;
- failed tasks.

### Tracing

Трассировать необходимо:

- HTTP-запросы;
- SQL-запросы;
- обращения к Redis;
- обращения к Object Storage;
- обращения к OpenSearch;
- фоновые задачи Celery.

## Security

Backend должен соблюдать следующие требования безопасности:

- пароли хранятся только в виде хэшей;
- использовать Argon2 или bcrypt;
- JWT access token короткоживущий;
- refresh token должен ротироваться;
- refresh token хранится безопасно;
- CORS ограничен whitelist-ом;
- rate limiting для auth endpoints;
- защита от brute force;
- email verification;
- валидация всех входных данных;
- проверка прав доступа на уровне сервисов;
- запрет загрузки исполняемых файлов;
- проверка MIME-типа файлов;
- ограничение размера загрузок;
- секреты не хранятся в Git;
- настройки приходят через env;
- в production отключён debug.

## Background jobs

Для фоновых задач используется Celery.

Типовые очереди:

```
default
emails
images
notifications
search-index
shopping-lists
```

Примеры задач:

- отправка письма подтверждения email;
- генерация thumbnail;
- индексация рецепта в OpenSearch;
- пересчёт списка покупок;
- отправка уведомлений подписчикам;
- очистка истёкших refresh tokens.

## Работа с файлами

Фотографии рецептов и аватары пользователей хранятся в Object Storage.

Backend не должен сохранять пользовательские файлы в контейнере.

Подход:

1. 1.Backend валидирует запрос на загрузку.
2. 2.Backend выдаёт pre-signed URL.
3. 3.Клиент загружает файл напрямую в Object Storage.
4. 4.Backend сохраняет metadata файла.
5. 5.Worker генерирует thumbnail.

Для local-окружения используется MinIO.

Для cloud-окружений используется Yandex Object Storage.

## Поиск

Для advanced-варианта используется OpenSearch.

Backend отвечает за:

- индексацию рецептов;
- обновление индекса при изменении рецепта;
- удаление из индекса при скрытии или удалении;
- поиск по названию;
- поиск по ингредиентам;
- фильтры;
- сортировку;
- исключение ингредиентов.

Для упрощённого начального этапа допустимо использовать PostgreSQL full-text search.

## Kubernetes

В Kubernetes backend запускается как Deployment.

Требования:

- минимум 2 реплики в production;
- readinessProbe;
- livenessProbe;
- resource requests;
- resource limits;
- env из ConfigMap и Secret;
- запуск от non-root пользователя;
- graceful shutdown;
- отдельный ServiceAccount;
- NetworkPolicy;
- PodDisruptionBudget;
- HorizontalPodAutoscaler.

Миграции выполняются отдельным Kubernetes Job:

```
alembic upgrade head
```

## CI/CD

Backend участвует в GitHub Actions pipelines.

На Pull Request должны выполняться:

- установка зависимостей;
- lint;
- type check;
- unit tests;
- Docker build;
- security scan.

На deploy pipeline:

- сборка Docker image;
- push в GHCR;
- запуск миграций;
- deploy через Helm;
- smoke tests.

## Smoke tests

Минимальные smoke tests после деплоя:

``` http
GET /health
GET /ready
GET /api/docs
```

Дополнительно:

- регистрация тестового пользователя в dev/staging;
- login;
- запрос списка рецептов;
- проверка доступа к базе данных.

## Полезные команды

Запуск dev-сервера:

```
uvicorn app.main:app --reload
```

Применить миграции:

```
alembic upgrade head
```

Создать миграцию:

```
alembic revision --autogenerate -m "message"
```

Запустить тесты:

```
pytest
```

Проверить стиль:

```
ruff check .
```

Форматировать код:

```
ruff format .
```

Проверить типы:

```
mypy app
```

Собрать Docker image:

```
docker build -t recipe-backend:local .
```

## Что уже реализовано

### Инициализация проекта (feat/backend-fastapi-init)

- Виртуальное окружение `.venv` (Python 3.12)
- `requirements.txt` — зафиксированные зависимости приложения
- `requirements-dev.txt` — инструменты разработки (ruff, mypy, pytest)
- `pyproject.toml` — конфигурация ruff, mypy, pytest

Структура пакета `app/`:

```
app/
  __init__.py
  main.py
  api/
  core/
  db/
  models/
  schemas/
  services/
  repositories/
tests/
```

Запущенные endpoints:

- `GET /health` → `{"status": "ok"}`
- `GET /ready` → `{"status": "ready"}`
- `GET /api/docs` — Swagger UI (OpenAPI)
- `GET /api/openapi.json` — OpenAPI schema

## Статус

Backend находится в разработке.

Приоритет реализации:

1. ~~Базовая структура FastAPI.~~ ✓
2. Конфигурация приложения.
3. 3.PostgreSQL и SQLAlchemy.
4. 4.Alembic.
5. 5.Auth.
6. 6.Users и profiles.
7. 7.Recipes CRUD.
8. 8.Uploads.
9. 9.Comments, likes, favorites.
10. 10.Meal plans и shopping lists.
11. 11.Search.
12. 12.Moderation и admin.
13. 13.Celery tasks.
14. 14.Observability.
15. 15.Security hardening.
