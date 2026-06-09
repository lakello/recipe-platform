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

Используемые инструменты:

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

### Подписки на авторов (feat/follows)

- `app/models/follow.py` — модель `Follow`: `follower_id`, `following_id`, уникальный составной индекс `uq_follow`, CASCADE-удаление
- `app/repositories/follow.py` — `FollowRepository`: get, create, delete, count_followers, count_following, list_followers, list_following, get_following_ids, is_following_batch; батч-методы исключают N+1 при листинге
- `app/services/follow.py` — `FollowService`: follow (400 самоподписка, 404 пользователь не найден, 409 уже подписан), unfollow, list_followers, list_following
- `app/schemas/follow.py` — `FollowUserRead` (id, username, avatar_url, is_following), `FollowUserPage`
- `app/api/follows.py` — роутер подписок
- `app/repositories/recipe.py` — добавлен `list_feed(author_ids, page, size)` для формирования ленты
- `tests/test_follow_service.py` — 8 unit-тестов
- `alembic/versions/i7a8b9c0d1e2` — создаёт таблицу `follows` с уникальным индексом

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `POST` | `/api/users/{id}/follow` | 🔒 | Подписаться на пользователя |
| `DELETE` | `/api/users/{id}/follow` | 🔒 | Отписаться |
| `GET` | `/api/users/{id}/followers` | — | Список подписчиков (пагинация) |
| `GET` | `/api/users/{id}/following` | — | Список подписок (пагинация) |
| `GET` | `/api/feed` | 🔒 | Лента рецептов от авторов из подписок |

### Публичные профили пользователей (feat/public-user-profiles)

- `app/schemas/user.py` — `UserPublicRead`: публичная схема (id, username, avatar_url, created_at); без email и приватных полей; дополнена `followers_count`, `following_count`, `is_following`
- `app/api/users.py` — `GET /api/users/{user_id}`: публичный endpoint с опциональной аутентификацией (`get_optional_user`); возвращает `UserPublicRead`, обогащённый follow-данными через `FollowRepository`

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/users/{user_id}` | опц. | Публичный профиль пользователя с подписками |

### Лайки и избранное (feat/likes-and-favorites)

- `app/models/like.py` — модели `Like` и `Favorite` с UniqueConstraint `(user_id, recipe_id)` и CASCADE-удалением
- `app/repositories/like.py` — `LikeRepository` (get, add, remove, count, count_batch, user_liked_batch) и `FavoriteRepository` (get, add, remove, list_by_user, user_favorited_batch); батч-методы исключают N+1 при листинге рецептов
- `app/services/like.py` — `LikeService` (like, unlike, get_status), `FavoriteService` (add_favorite, remove_favorite, list_favorites)
- `app/api/likes.py` — роутер эндпоинтов лайков и избранного
- `app/schemas/like.py` — `LikeStatus` (likes_count, is_liked), `FavoriteStatus` (is_favorited)
- `app/schemas/recipe.py` — `RecipeRead` дополнен `likes_count`, `is_liked`, `is_favorited`
- `app/services/recipe.py` — `_enrich_single` / `_enrich_batch` добавляют данные вовлечённости к рецептам
- `tests/test_like_service.py` — 13 unit-тестов
- `alembic/versions/g5e6f7a8b1c2` — создаёт таблицы `likes` и `favorites` с индексами
- `backend/scripts/check_alembic_heads.py` — скрипт для pre-commit хука, проверяет единственность Alembic head (без подключения к БД)

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `POST` | `/api/recipes/{id}/like` | 🔒 | Поставить лайк (409 при повторе) |
| `DELETE` | `/api/recipes/{id}/like` | 🔒 | Убрать лайк |
| `GET` | `/api/recipes/{id}/like` | опц. | Счётчик лайков и статус текущего пользователя |
| `POST` | `/api/recipes/{id}/favorite` | 🔒 | Добавить в избранное (409 при повторе) |
| `DELETE` | `/api/recipes/{id}/favorite` | 🔒 | Удалить из избранного |
| `GET` | `/api/users/me/favorites` | 🔒 | Список избранных рецептов |

### Комментарии (feat/comments)

- `app/models/comment.py` — модель `Comment`: `body`, `parent_id` (одноуровневые ответы), `is_hidden`, `is_deleted` (soft delete), FK на `recipes` и `users` с CASCADE
- `app/repositories/comment.py` — `CommentRepository`: create, get_by_id, list_top_level (с пагинацией и счётчиком), list_replies, update, reply_count_batch (батч-подсчёт ответов без N+1)
- `app/services/comment.py` — `CommentService`: add_comment (с валидацией parent), edit_comment, delete_comment (soft), hide_comment, unhide_comment, list_comments, list_replies; ответ на ответ запрещён (400)
- `app/api/comments.py` — роутер комментариев
- `app/api/deps.py` — добавлена зависимость `get_current_moderator` (admin или superadmin)
- `app/schemas/comment.py` — `CommentRead` с `model_validator`: тело скрытого комментария заменяется на placeholder; `CommentPage` для пагинации
- `tests/test_comment_service.py` — 14 unit-тестов
- `alembic/versions/h6f7a8b9c1d2` — создаёт таблицу `comments` с индексами

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `POST` | `/api/recipes/{id}/comments` | 🔒 | Оставить комментарий или ответ |
| `GET` | `/api/recipes/{id}/comments` | — | Список комментариев (пагинация) |
| `GET` | `/api/comments/{id}/replies` | — | Список ответов на комментарий |
| `PATCH` | `/api/comments/{id}` | 🔒 автор | Редактировать свой комментарий |
| `DELETE` | `/api/comments/{id}` | 🔒 автор | Удалить свой комментарий (soft delete, 204) |
| `POST` | `/api/comments/{id}/hide` | 🔒 модератор | Скрыть комментарий |
| `POST` | `/api/comments/{id}/unhide` | 🔒 модератор | Показать скрытый комментарий |

### Загрузка фото (feat/uploads)

- `app/models/photo.py` — модель `RecipePhoto`: `key` (путь в Object Storage), `content_type`, FK на `recipes`
- `app/repositories/photo.py` — `upsert` (одно фото на рецепт), `get_by_recipe`, `delete`
- `app/services/upload.py` — `presign_upload`, `attach_recipe_photo`, `delete_recipe_photo`, `set_avatar`
- `app/core/storage.py` — boto3-клиент для MinIO/S3; presigned URL подписываются с `s3_public_url` (иначе подпись не совпадёт с хостом браузера)
- `app/schemas/upload.py` — `PresignRequest`, `PresignResponse`, `AttachPhotoRequest`
- `app/tasks/thumbnails.py` — заглушка Celery-задачи `generate_thumbnail` (будет реализована позже)

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `POST` | `/api/uploads/presign` | 🔒 | Получить presigned PUT URL для загрузки файла |
| `POST` | `/api/uploads/recipes/{id}/photo` | 🔒 автор | Привязать загруженное фото к рецепту |
| `DELETE` | `/api/uploads/recipes/{id}/photo` | 🔒 автор | Удалить фото рецепта |
| `POST` | `/api/uploads/avatar` | 🔒 | Установить аватар пользователя |
| `GET` | `/api/uploads/view?key=` | — | Редирект на presigned GET URL фото |

Сценарий загрузки:
1. Клиент запрашивает presigned URL (`POST /api/uploads/presign`)
2. Клиент загружает файл напрямую в MinIO (`PUT <presigned_url>`)
3. Клиент сообщает бэкенду ключ файла (`POST /api/uploads/recipes/{id}/photo`)
4. Бэкенд сохраняет metadata и ставит задачу на генерацию thumbnail

Переменные окружения:

| Переменная | Описание |
|---|---|
| `S3_ENDPOINT_URL` | Внутренний URL MinIO (для API-операций) |
| `S3_PUBLIC_URL` | Публичный URL MinIO (для presigned URL браузера) |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | Credentials |
| `S3_BUCKET_PHOTOS` / `S3_BUCKET_AVATARS` | Имена бакетов |

### Ингредиенты и шаги (feat/ingredients-steps)

- `app/models/ingredient.py` — модели `Ingredient` (глобальный справочник), `RecipeIngredient` (связь с amount, unit enum, order), `RecipeStep` (order, title, description)
- `IngredientUnit` enum: значения в БД — `g`, `kg`, `ml`, `l`, `tsp`, `tbsp`, `pcs`, `cup`, `pinch`, `to_taste`; колонка использует `values_callable` чтобы SQLAlchemy биндил значения, а не имена членов enum
- `app/repositories/ingredient.py` — `get_or_create`, `search`, `replace_recipe_ingredients`, `replace_recipe_steps`
- `app/services/ingredient.py` — `search_ingredients`, `set_ingredients`, `set_steps` с проверкой авторства
- `app/api/ingredients.py` — роутеры для поиска ингредиентов и сохранения ингредиентов/шагов
- `app/schemas/recipe.py` — `RecipeRead` дополнен `ingredients` и `steps`
- `tests/test_ingredient_service.py` — 6 unit-тестов
- `alembic/versions/f4d5e6f7a1b2` — создаёт `ingredients`, `recipe_ingredients`, `recipe_steps`

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/ingredients?search=` | — | Поиск ингредиентов в справочнике |
| `PUT` | `/api/recipes/{id}/ingredients` | 🔒 автор | Заменить все ингредиенты рецепта |
| `PUT` | `/api/recipes/{id}/steps` | 🔒 автор | Заменить все шаги рецепта |

### Категории (feat/categories)

- `app/models/user.py` — добавлен `UserRole` enum (`user`, `admin`, `superadmin`) и поле `role`
- `app/models/category.py` — модель `Category`: `name`, `slug` (auto-генерация), `description`
- `app/repositories/category.py` — create, get_by_id, get_by_slug, list_all, update, delete
- `app/services/category.py` — CRUD с проверкой уникальности slug; функция `_slugify`
- `app/api/deps.py` — зависимости `get_current_admin`, `get_current_superadmin`
- `app/api/categories.py` — роутер `/api/categories`
- `app/schemas/recipe.py` — добавлен `category_id` и вложенный `CategoryRead`
- `tests/test_category_service.py` — 8 unit-тестов

Миграции:
- `c1a2b3d4e5f6` — добавляет `role` в таблицу `users`
- `d2b3c4e5f6a1` — создаёт таблицу `categories`
- `e3c4d5f6a1b2` — добавляет `category_id` FK в `recipes`

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/categories` | — | Список категорий |
| `GET` | `/api/categories/{id}` | — | Получить категорию |
| `POST` | `/api/categories` | 🔒 admin | Создать категорию |
| `PATCH` | `/api/categories/{id}` | 🔒 admin | Редактировать категорию |
| `DELETE` | `/api/categories/{id}` | 🔒 admin | Удалить категорию |
| `GET` | `/api/recipes?category_id=` | опц. | Фильтр рецептов по категории |

Назначение ролей (через SQL):
```sql
UPDATE users SET role = 'superadmin' WHERE email = 'your@email.com';
```

### OAuth Google и Яндекс (feat/oauth-google-yandex)

- `app/models/oauth_account.py` — модель `UserOAuthAccount`: `provider`, `provider_user_id`, FK на `users` с CASCADE; уникальное ограничение `(provider, provider_user_id)`
- `app/models/user.py` — `password_hash` сделан nullable для поддержки OAuth-only пользователей
- `app/repositories/oauth_account.py` — `OAuthAccountRepository`: поиск по провайдеру и `provider_user_id`, создание
- `app/services/oauth.py` — `OAuthService`: обмен authorization code на access token (aiohttp), получение профиля, поиск существующего OAuth-аккаунта, привязка по email или автосоздание нового пользователя, выдача JWT; CSRF-защита через state-параметр
- `app/api/oauth.py` — OAuth endpoints; state хранится в short-lived httpOnly cookie (5 мин); при ошибке — редирект на `/login?error=oauth_error`; при успехе — установка auth cookies и редирект на `FRONTEND_URL`
- `alembic/versions/m1e2f3a4b5c6` — создаёт таблицу `user_oauth_accounts`; делает `password_hash` nullable
- `app/core/config.py` — добавлены OAuth credentials и `FRONTEND_URL`
- `docker-compose.yml` — OAuth переменные и `FRONTEND_URL` передаются в контейнер backend
- `infra/k8s/oauth-secrets.example.yaml` — шаблон Kubernetes Secret для OAuth credentials

Endpoints:

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/auth/google/login` | Редирект на Google OAuth |
| `GET` | `/api/auth/google/callback` | Обработка Google callback |
| `GET` | `/api/auth/yandex/login` | Редирект на Яндекс OAuth |
| `GET` | `/api/auth/yandex/callback` | Обработка Яндекс callback |

Логика привязки аккаунтов:
- Есть `UserOAuthAccount` для данного провайдера → логин
- Нет, но email совпадает → привязка OAuth к существующему аккаунту
- Email новый → создание пользователя (username генерируется из имени профиля)

Переменные окружения:

| Переменная | Описание |
|---|---|
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth credentials |
| `GOOGLE_REDIRECT_URI` | Callback URI (по умолчанию `http://localhost:8000/api/auth/google/callback`) |
| `YANDEX_CLIENT_ID` / `YANDEX_CLIENT_SECRET` | Яндекс OAuth credentials |
| `YANDEX_REDIRECT_URI` | Callback URI (по умолчанию `http://localhost:8000/api/auth/yandex/callback`) |
| `FRONTEND_URL` | URL фронтенда для редиректа после OAuth (по умолчанию `http://localhost:5173`) |

### Роли, модерация и админка (feat/admin-moderation)

- `app/models/user.py` — `UserRole` enum расширен значением `moderator` (итого: `user`, `moderator`, `admin`, `superadmin`)
- `app/models/report.py` — модель `Report`: `reporter_id`, `target_type` (`recipe`/`comment`/`user`), `target_id` (UUID), `reason` (`spam`/`offensive`/`misinformation`/`other`), `description`, `status` (`pending`/`reviewed`/`dismissed`)
- `app/models/moderation_action.py` — модель `ModerationAction`: аудит-запись каждого действия модератора; `action_type` enum: `hide_recipe`, `unhide_recipe`, `hide_comment`, `unhide_comment`, `block_user`, `unblock_user`, `assign_role`, `resolve_report`, `dismiss_report`
- `app/repositories/report.py` / `moderation_action.py` — стандартный CRUD
- `app/repositories/user.py` — `list_all(search, role)`: поиск по username/email, фильтр по роли
- `app/repositories/recipe.py` — `list_all_admin(search, has_comments)`: поиск по названию/автору, фильтр рецептов с комментариями
- `app/repositories/comment.py` — `list_all_admin(recipe_id, search, status)`: фильтры по рецепту, тексту, статусу
- `app/schemas/admin.py` — схемы: `AdminUserRead/Page`, `AdminRecipeRead/Page` (с вложенным автором включая email), `AdminCommentRead/Page` (с `parent_id` и автором), `ReportCreate/Read/Page`, `AssignRoleRequest`, `BlockRequest`, `HideRequest`
- `app/schemas/user.py` — добавлено поле `role` в `UserPublicRead`
- `app/schemas/recipe.py` — добавлено поле `role` в `RecipeAuthorRead`
- `app/schemas/comment.py` — добавлено поле `role` в `CommentAuthor`
- `app/services/admin.py` — `AdminService`: list_users, assign_role (с иерархией прав), block_user, unblock_user, create_report, list_reports, review_report, dismiss_report, list_recipes_admin, hide_recipe, unhide_recipe, list_comments_admin, delete_comment_admin; аудит каждого действия через `_log()`
- `app/api/deps.py` — добавлен `get_current_superadmin`
- `app/api/admin.py` — роутер `/api/admin`
- `scripts/seed_admin.py` — создаёт или обновляет суперадмина из env-переменных `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_USERNAME`
- `tests/test_admin_service.py` — 15 unit-тестов
- `alembic/versions/n2f3a4b5c6d7` — добавляет `moderator` в enum `userrole`, `is_hidden` в таблицу `recipes`, создаёт таблицы `reports` и `moderation_actions`

Иерархия ролей:
- **superadmin** — все права; может назначать `user/moderator/admin`; может блокировать пользователей (кроме других superadmin); superadmin назначается только вручную через БД
- **admin** — скрывает/удаляет рецепты и комментарии; назначает `user/moderator`; не может трогать других admin и superadmin
- **moderator** — скрывает рецепты и комментарии; обрабатывает жалобы

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/admin/users` | 🔒 admin | Список пользователей с поиском и фильтром по роли |
| `POST` | `/api/admin/users/{id}/role` | 🔒 admin | Назначить роль |
| `POST` | `/api/admin/users/{id}/block` | 🔒 superadmin | Заблокировать пользователя |
| `POST` | `/api/admin/users/{id}/unblock` | 🔒 superadmin | Разблокировать пользователя |
| `POST` | `/api/admin/reports` | 🔒 | Подать жалобу |
| `GET` | `/api/admin/reports` | 🔒 moderator | Список жалоб с фильтром по статусу |
| `POST` | `/api/admin/reports/{id}/review` | 🔒 moderator | Принять жалобу |
| `POST` | `/api/admin/reports/{id}/dismiss` | 🔒 moderator | Отклонить жалобу |
| `GET` | `/api/admin/recipes` | 🔒 moderator | Список рецептов с поиском; `has_comments=true` — только с комментариями |
| `POST` | `/api/admin/recipes/{id}/hide` | 🔒 moderator | Скрыть рецепт |
| `POST` | `/api/admin/recipes/{id}/unhide` | 🔒 moderator | Показать рецепт |
| `GET` | `/api/admin/comments` | 🔒 moderator | Список комментариев с фильтрами |
| `POST` | `/api/admin/comments/{id}/delete` | 🔒 moderator | Удалить комментарий (soft delete) |

Запуск seed-скрипта:
```bash
docker compose exec backend sh -c "ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=secret python scripts/seed_admin.py"
```

### Список покупок (feat/shopping-list)

- `app/models/ingredient_category.py` — модель `IngredientCategory`: `name` (unique), `created_at`
- `app/models/shopping_list.py` — модели `ShoppingList` (один на пользователя, unique FK) и `ShoppingListItem` (`name`, `amount`, `unit`, `is_bought`, `is_manual`, `ingredient_id` nullable FK)
- `app/repositories/ingredient_category.py` / `app/services/ingredient_category.py` — CRUD категорий ингредиентов (409 при дубликате)
- `app/repositories/shopping_list.py` — `get_or_create_list`, `get_item`, `get_item_by_ingredient`, `add_item`, `update_item`, `delete_item`, `get_meal_plan_items_for_dates` (группирует даты по неделям для эффективного OR-запроса)
- `app/services/shopping_list.py` — умный merge: нормализация единиц (kg↔g, l↔ml), `max(existing, generated)` — добавляет только разницу; генерация из 3 режимов (today, week, custom); CRUD элементов
- `app/tasks/shopping_list.py` — Celery-таск `tasks.generate_shopping_list`: запускает async-сервис через `asyncio.run()` внутри синхронного воркера
- `app/models/__init__.py` — импортирует все модули моделей, чтобы SQLAlchemy резолвил все relationship-ссылки до маппинга (нужно для Celery-воркера)
- `app/api/ingredient_categories.py` — роутер `/api/ingredient-categories`
- `app/api/shopping_list.py` — роутер `/api/shopping-list`; генерация асинхронная (202 + task_id); polling статуса через Celery result backend (Redis DB 2)
- `app/celery_app.py` — включён result backend (`CELERY_RESULT_BACKEND_URL`); результаты хранятся 1 час
- `tests/test_shopping_list_service.py` — 21 тест: unit (нормализация единиц, режимы дат) + integration (merge-алгоритм)
- Миграции: `k9c0d1e2f3a4` (ingredient_categories + FK в ingredients), `l0d1e2f3a4b5` (shopping_lists, shopping_list_items)

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/ingredient-categories` | — | Список категорий ингредиентов |
| `POST` | `/api/ingredient-categories` | 🔒 admin | Создать категорию |
| `PATCH` | `/api/ingredient-categories/{id}` | 🔒 admin | Редактировать категорию |
| `DELETE` | `/api/ingredient-categories/{id}` | 🔒 admin | Удалить категорию |
| `GET` | `/api/shopping-list` | 🔒 | Текущий список покупок пользователя |
| `POST` | `/api/shopping-list/generate` | 🔒 | Запустить генерацию (202, возвращает `task_id`) |
| `GET` | `/api/shopping-list/generate/status/{task_id}` | 🔒 | Статус задачи генерации (polling) |
| `POST` | `/api/shopping-list/items` | 🔒 | Добавить элемент вручную |
| `PATCH` | `/api/shopping-list/items/{id}` | 🔒 | Обновить элемент (количество, единица, is_bought) |
| `DELETE` | `/api/shopping-list/items/{id}` | 🔒 | Удалить элемент |

Переменные окружения:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `CELERY_RESULT_BACKEND_URL` | `redis://localhost:6379/2` | Redis DB для хранения результатов Celery-задач |

### План питания (feature/meal-plan)

- `app/models/meal_plan.py` — модели `MealPlan` (неделя пользователя, уникальный `(user_id, week_start)`) и `MealPlanItem` (`recipe_id`, `day_of_week`, `meal_type`, `servings`)
- `app/repositories/meal_plan.py` — `get_or_create_week`, `add_item`, `get_item`, `update_item`, `delete_item`, `get_items_for_week`, `copy_week`
- `app/services/meal_plan.py` — `get_week`, `add_item`, `update_item`, `delete_item`, `copy_from_week`; проверка владельца элемента
- `app/schemas/meal_plan.py` — `MealPlanRead`, `MealPlanItemRead/Create/Update`, `CopyFromWeekRequest`
- `app/api/meal_plans.py` — роутер `/api/meal-plans`
- `tests/test_meal_plan_service.py` — unit-тесты сервиса

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/meal-plans/week?week_start=` | 🔒 | Получить план на неделю |
| `POST` | `/api/meal-plans/items` | 🔒 | Добавить блюдо в план |
| `PATCH` | `/api/meal-plans/items/{id}` | 🔒 | Обновить блюдо (порции, тип приёма пищи) |
| `DELETE` | `/api/meal-plans/items/{id}` | 🔒 | Удалить блюдо из плана |
| `POST` | `/api/meal-plans/copy-week` | 🔒 | Скопировать план из выбранной недели в текущую |

### Поиск рецептов (feat/search)

- `app/core/opensearch.py` — `AsyncOpenSearch`-клиент, маппинг индекса `recipes` (title, description, ingredient_names, category, cooking_time_minutes, difficulty, status, visibility, likes_count)
- `app/services/search.py` — `SearchService`: `index_recipe` (пропускает непубличные/не-published → удаляет из индекса), `remove_recipe`, `search` с построением `bool`-запроса
- `app/api/search.py` — `GET /api/search/recipes`: полнотекстовый поиск, фильтры, исключение ингредиентов, сортировка, пагинация; возвращает полные `RecipeRead` из БД по ids из OpenSearch
- `app/schemas/search.py` — `SearchParams`, `SearchResult`
- `app/api/recipes.py` — хуки: `index_recipe` при create/update, `remove_recipe` при delete
- `app/main.py` — `os_client` инициализируется в lifespan, создаёт индекс при старте
- `tests/test_search_service.py` — 9 unit-тестов
- `scripts/reindex_opensearch.py` — разовый скрипт переиндексации всех существующих рецептов

Endpoint:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/search/recipes` | опц. | Поиск рецептов по названию, ингредиентам, категории, сложности, времени; исключение ингредиентов; сортировка; пагинация |

Параметры поиска: `q`, `category_id`, `min_time`, `max_time`, `difficulty`, `include_ingredients[]`, `exclude_ingredients[]`, `sort` (relevance/newest/popular), `page`, `size`.

### Уведомления (feat/notifications)

- `app/models/notification.py` — модель `Notification`: `user_id`, `actor_id`, `type` (like/comment/reply/follow/moderation), `entity_id`, `entity_type`, `body`, `is_read`; `actor` загружается через `lazy="selectin"`
- `app/models/notification_preferences.py` — модель `NotificationPreferences`: email-флаги по типам (like/comment/follow)
- `app/repositories/notification.py` — `NotificationRepository`: create, get_by_id, list_for_user, mark_read, mark_all_read, count_unread
- `app/repositories/notification_preferences.py` — `NotificationPreferencesRepository`: get_or_default, update
- `app/services/notification.py` — `NotificationService`: list, mark_read, mark_all_read, count_unread, create_like_notification (без уведомления себе), create_comment_notification (comment или reply в зависимости от parent_id), create_follow_notification, create_moderation_notification
- `app/api/notifications.py` — роутер уведомлений
- `app/api/likes.py`, `app/api/comments.py`, `app/api/follows.py`, `app/api/admin.py` — вызов `create_*_notification` + `send_notification_email.delay()` после успешного действия
- `app/tasks/email.py` — Celery-задача `tasks.send_notification_email`: загружает уведомление из БД, проверяет email-настройки пользователя, отправляет письмо через SMTP; retry до 5 раз с exponential backoff (max 600s)
- `app/core/config.py` — добавлены SMTP-настройки (`smtp_host`, `smtp_port`, `smtp_tls`, `smtp_user`, `smtp_password`, `smtp_from`) и `email_notifications_enabled`
- `docker-compose.yml` — добавлен сервис `mailhog` (SMTP :1025, Web UI :8025); добавлены `SMTP_HOST`/`SMTP_PORT` в окружение `celery-worker`
- `alembic/versions/o3g4h5i6j7k8` — создаёт таблицу `notifications` с enum `notification_type`
- `alembic/versions/p4h5i6j7k8l9` — создаёт таблицу `notification_preferences`

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `GET` | `/api/notifications` | 🔒 | Список уведомлений с пагинацией и счётчиком непрочитанных |
| `GET` | `/api/notifications/unread-count` | 🔒 | Количество непрочитанных |
| `PATCH` | `/api/notifications/{id}/read` | 🔒 | Отметить одно уведомление прочитанным |
| `PATCH` | `/api/notifications/read-all` | 🔒 | Отметить все прочитанными |
| `GET` | `/api/notifications/preferences` | 🔒 | Получить email-настройки |
| `PATCH` | `/api/notifications/preferences` | 🔒 | Обновить email-настройки |

Переменные окружения:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `SMTP_HOST` | `localhost` | SMTP-сервер (в Docker — `mailhog`) |
| `SMTP_PORT` | `1025` | SMTP-порт |
| `SMTP_FROM` | `noreply@recipe-platform.local` | Адрес отправителя |
| `SMTP_TLS` | `false` | Использовать TLS |
| `EMAIL_NOTIFICATIONS_ENABLED` | `true` | Включить email-уведомления |

Для просмотра писем в dev-окружении: `http://localhost:8025` (Mailhog Web UI).

### Docker (feat/docker-compose-local)

- `Dockerfile` — `python:3.12-slim`, кэш зависимостей (requirements.txt отдельным слоем), применение миграций и запуск uvicorn в одной CMD через `sh -c`
- `.dockerignore` — исключены `__pycache__`, `*.pyc`, `.pytest_cache`, `*.egg-info`, `.env`, `.git`

Сборка и запуск через Docker Compose из корня проекта:

```bash
cp .env.example .env   # заполнить переменные
docker compose up --build
```

### Базовый CRUD рецептов (feat/backend-recipes)

- `app/models/recipe.py` — модель `Recipe` с enum-полями: `RecipeStatus` (draft/published/deleted), `RecipeVisibility` (public/private), `Difficulty` (easy/medium/hard)
- `alembic/versions/af66781aeaf9` — миграция создаёт таблицу `recipes` с FK на `users`
- `app/repositories/recipe.py` — create, get_by_id, list_visible, update, soft delete
- `app/services/recipe.py` — CRUD с проверкой прав автора и правилами видимости
- `app/api/deps.py` — добавлен `get_optional_user` для публичных endpoints
- `app/api/recipes.py` — роутер с prefix `/api/recipes`
- `tests/test_recipe_service.py` — 11 unit-тестов

Endpoints:

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| `POST` | `/api/recipes` | 🔒 | Создать рецепт |
| `GET` | `/api/recipes` | опц. | Список публичных рецептов + своих |
| `GET` | `/api/recipes/{id}` | опц. | Получить рецепт |
| `PATCH` | `/api/recipes/{id}` | 🔒 автор | Редактировать рецепт |
| `DELETE` | `/api/recipes/{id}` | 🔒 автор | Удалить рецепт (soft delete) |

### Регистрация и логин (feat/backend-auth)

- `app/core/security.py` — создание/валидация JWT access token, генерация refresh token
- `app/models/refresh_token.py` — модель `RefreshToken` с FK на users, `expires_at`, `is_revoked`
- `alembic/versions/be4c1adff2ba` — миграция создаёт таблицу `refresh_tokens`
- `app/repositories/refresh_token.py` — create, get_by_token, revoke, is_valid
- `app/services/auth.py` — register, login, refresh (ротация), logout
- `app/api/deps.py` — dependency `get_current_user` для защищённых endpoints
- `app/api/auth.py` — роутер с prefix `/api/auth`
- `app/api/users.py` — роутер с prefix `/api/users`
- `tests/test_auth_service.py` — 9 unit-тестов

Endpoints:

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/auth/register` | Регистрация, возвращает токены |
| `POST` | `/api/auth/login` | Вход по email/паролю |
| `POST` | `/api/auth/refresh` | Обновление токенов с ротацией |
| `POST` | `/api/auth/logout` | Инвалидация refresh token |
| `GET` | `/api/users/me` | Данные текущего пользователя 🔒 |
| `PATCH` | `/api/users/me` | Обновление username 🔒 |

**Обновлено в feat/frontend-auth:**
- Токены устанавливаются в httpOnly cookies (`access_token`, `refresh_token`)
- `get_current_user` читает токен из cookie ИЛИ `Authorization: Bearer`
- CORS: `allow_credentials=True`

### Модель пользователей (feat/backend-user-model)

- `app/models/user.py` — SQLAlchemy-модель `User`: UUID pk, уникальные `email` и `username`, `bcrypt`-хэш пароля, флаги `is_active` / `is_email_verified`, timezone-aware timestamps
- `app/schemas/user.py` — `UserCreate` (валидация email, username 3–50 символов, пароль 8+), `UserRead` (без `password_hash`)
- `app/repositories/user.py` — `create`, `get_by_id`, `get_by_email`, `get_by_username`
- `app/services/user.py` — `create_user` (хэширование bcrypt, проверка уникальности → 409), `get_by_id`, `get_by_email`
- `alembic/versions/72dfc48e97a3` — миграция создаёт таблицу `users` с уникальными индексами
- `tests/test_user_service.py` — 7 unit-тестов сервиса с замоканным репозиторием

### Подключение PostgreSQL (feat/backend-postgresql)

- `app/db/base.py` — `DeclarativeBase` для всех будущих SQLAlchemy-моделей
- `app/db/session.py` — async SQLAlchemy движок (`psycopg_async`), фабрика сессий, dependency `get_db`
- `alembic/` — инициализирован и настроен на чтение `DATABASE_URL` из `Settings`
- `alembic/versions/dea71c5c548c_initial.py` — первая миграция, создаёт таблицу `alembic_version`
- `GET /ready` — теперь выполняет `SELECT 1` к БД, возвращает `503` если БД недоступна

Команды Alembic:

```bash
alembic upgrade head          # применить все миграции
alembic downgrade -1          # откатить последнюю миграцию
alembic revision --autogenerate -m "описание"  # создать новую миграцию
alembic current               # текущая ревизия
```

### Конфигурация приложения (feat/backend-app-config)

- `app/core/config.py` — класс `Settings` через pydantic-settings, все переменные читаются из `.env`
- `app/core/logging.py` — JSON-логирование в stdout, request_id в каждой строке лога
- `app/core/middleware.py` — Request ID middleware (asgi-correlation-id)
- `app/core/exceptions.py` — единые обработчики: HTTP-ошибки, ошибки валидации (422), непойманные исключения (500)
- `.env.example` — шаблон переменных окружения

Переменные окружения:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `APP_ENV` | `local` | Окружение (local/dev/staging/production) |
| `APP_NAME` | `recipe-platform-backend` | Имя приложения |
| `DATABASE_URL` | postgresql+psycopg://... | Строка подключения к PostgreSQL |
| `REDIS_URL` | redis://localhost:6379/0 | Строка подключения к Redis |
| `JWT_SECRET` | — | Секрет для подписи JWT |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Время жизни access token |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Время жизни refresh token |
| `CORS_ORIGINS` | localhost:3000, localhost:5173 | Разрешённые CORS-источники (JSON-массив) |

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
2. ~~Конфигурация приложения.~~ ✓
3. ~~PostgreSQL и SQLAlchemy.~~ ✓
4. ~~Alembic.~~ ✓
5. ~~Auth (регистрация, логин, JWT, refresh).~~ ✓
6. ~~Users и profiles (модель).~~ ✓
7. ~~Recipes CRUD.~~ ✓
8. ~~Категории + роли пользователей.~~ ✓
9. ~~Ингредиенты и шаги приготовления.~~ ✓
10. ~~Uploads (presigned URL, привязка фото, аватары).~~ ✓
11. ~~Likes, favorites.~~ ✓
12. ~~Comments.~~ ✓
13. ~~Public user profiles.~~ ✓
14. ~~Follows и feed.~~ ✓
15. ~~Search (OpenSearch).~~ ✓
16. ~~Meal plans и shopping lists.~~ ✓
17. ~~OAuth Google и Яндекс.~~ ✓
18. ~~Moderation и admin.~~ ✓
19. ~~Уведомления и email-доставка (Celery).~~ ✓
20. Observability.
21. Security hardening.
