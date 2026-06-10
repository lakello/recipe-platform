# Recipe Platform

Платформа для рецептов и планирования питания — production-like DevOps pet-проект advanced-уровня.

Сервис позволяет пользователям публиковать рецепты, искать блюда по ингредиентам, планировать питание на неделю и автоматически формировать список покупок.

Проект разрабатывается как полноценное приложение с современной инфраструктурой, CI/CD, Kubernetes, мониторингом, логированием, безопасностью и несколькими окружениями.

## Статус разработки

| Компонент | Статус |
|---|---|
| Backend: инициализация FastAPI | ✅ Готово |
| Backend: конфигурация приложения | ✅ Готово |
| Backend: база данных (PostgreSQL + SQLAlchemy) | ✅ Готово |
| Backend: Alembic миграции | ✅ Готово |
| Backend: модель пользователей | ✅ Готово |
| Backend: Auth | ✅ Готово |
| Backend: базовый CRUD рецептов | ✅ Готово |
| Frontend: инициализация React | ✅ Готово |
| Frontend: Auth страницы | ✅ Готово |
| Frontend: базовые рецепты (список, детали, создание, редактирование) | ✅ Готово |
| Docker Compose для локального запуска | ✅ Готово |
| Backend + Frontend: категории, роли пользователей | ✅ Готово |
| Backend + Frontend: ингредиенты и шаги приготовления | ✅ Готово |
| Backend + Frontend: загрузка фото рецептов и аватаров | ✅ Готово |
| Backend + Frontend: лайки и избранное | ✅ Готово |
| Backend + Frontend: комментарии с ответами и модерацией | ✅ Готово |
| Backend + Frontend: публичные профили пользователей и редизайн карточек рецептов | ✅ Готово |
| Backend + Frontend: подписки на авторов и лента | ✅ Готово |
| Backend + Frontend: поиск рецептов (OpenSearch) | ✅ Готово |
| Backend + Frontend: план питания на неделю | ✅ Готово |
| Backend + Frontend: список покупок (async Celery + polling) | ✅ Готово |
| Backend + Frontend: OAuth Google и Яндекс | ✅ Готово |
| Backend + Frontend: модерация и админ-панель | ✅ Готово |
| Backend + Frontend: уведомления и email-доставка | ✅ Готово |
| Android | ⏳ Планируется |
| Desktop | ⏳ Планируется |
| Инфраструктура: Terraform базовая структура | ✅ Готово |
| Инфраструктура: Terraform модуль network (VPC, subnets, NAT, security groups) | ✅ Готово |
| Инфраструктура: Terraform модуль kubernetes (Managed K8s, node groups, autoscaling) | ✅ Готово |
| Инфраструктура: Terraform модули (postgres, redis, ...) | ⏳ Планируется |
| Инфраструктура: Ansible, Helm, CI/CD | ⏳ Планируется |
| CI/CD | ⏳ Планируется |

## Цели проекта

Основная цель проекта — на практике реализовать полный цикл разработки, доставки и эксплуатации приложения с использованием современного DevOps-стека.

В проекте используются технологии не «для галочки», а для решения реальных задач:

- контейнеризация приложения;
- локальная разработка;
- автоматическая сборка и тестирование;
- доставка Docker-образов;
- развёртывание в Kubernetes;
- управление облачной инфраструктурой;
- настройка Linux-серверов;
- мониторинг, логирование и алертинг;
- безопасное хранение секретов;
- backup и rollback.

## Основной стек

### Application

- Backend: Python 3.12, FastAPI
- Frontend: React, TypeScript, Vite
- Android: Kotlin, Jetpack Compose
- Desktop: Tauri, React, Rust runtime
- Database: PostgreSQL
- Cache / Broker: Redis
- Search: OpenSearch
- Background jobs: Celery
- Object Storage: Yandex Object Storage

### DevOps / Infrastructure

- Docker
- Docker Compose
- Linux
- Git
- GitHub Actions
- GitHub Container Registry
- Terraform
- Ansible
- Kubernetes
- Yandex Managed Kubernetes
- Helm
- Nginx Ingress Controller
- cert-manager
- Prometheus
- Grafana
- Loki
- OpenTelemetry
- Tempo или Jaeger
- Alertmanager

### Cloud

Основное облако проекта:

- Yandex Cloud

Используемые сервисы:

- Yandex Managed Kubernetes
- Yandex Managed PostgreSQL
- Yandex Managed Redis
- Yandex Object Storage
- Yandex VPC
- Yandex DNS
- Yandex Lockbox
- Yandex Compute Cloud
- Yandex Monitoring
- Yandex Cloud Logging

## Окружения

Проект поддерживает несколько окружений:

| Окружение | Назначение |
|---|---|
| `local` | Локальная разработка через Docker Compose |
| `dev` | Автоматический деплой из ветки `develop` |
| `staging` | Production-like окружение для финальной проверки релизов |
| `production` | Публичное стабильное окружение |

## Возможности приложения

### Пользователи

- регистрация по email и паролю;
- вход через Google OAuth;
- вход через Яндекс OAuth;
- JWT access token;
- refresh token;
- профиль пользователя;
- аватар;
- публичный профиль автора;
- роли пользователей.

### Роли

В системе используются роли:

- гость;
- пользователь;
- автор;
- модератор;
- администратор.

### Рецепты

Пользователь может:

- создавать рецепты;
- редактировать свои рецепты;
- загружать фотографии;
- указывать ингредиенты;
- описывать шаги приготовления;
- задавать категорию, теги, сложность, КБЖУ;
- делать рецепт публичным, приватным или черновиком;
- удалять рецепт.

Статусы рецепта:

- `Draft`;
- `Public`;
- `Private`;
- `Hidden`;
- `Deleted`.

### Социальные функции

- лайки;
- избранное;
- комментарии;
- ответы на комментарии;
- подписки на авторов;
- уведомления;
- жалобы на контент.

### Планирование питания

Пользователь может:

- составлять недельный план питания;
- добавлять рецепты на конкретный день (из поиска или прямо со страницы рецепта);
- выбирать тип приёма пищи (завтрак, обед, ужин, перекус);
- менять количество порций;
- удалять блюда из плана;
- копировать план из любой другой недели;
- переходить на страницу рецепта прямо из плана питания;
- очищать план.

### Список покупок

Система автоматически формирует список покупок на основе недельного плана питания.

Алгоритм:

1. Получить рецепты из плана питания.
2. Извлечь ингредиенты.
3. Пересчитать количество с учётом порций.
4. Объединить одинаковые ингредиенты.
5. Сгруппировать продукты по категориям.
6. Сформировать итоговый список покупок.

### Модерация и администрирование

Модератор может:

- просматривать жалобы;
- скрывать рецепты;
- скрывать или удалять комментарии;
- отправлять предупреждения;
- просматривать историю модерации.

Администратор может:

- управлять пользователями;
- назначать роли;
- управлять категориями;
- просматривать аудит;
- управлять системными настройками.

## Архитектура

Рекомендуемый архитектурный стиль — модульный монолит с возможностью дальнейшего выделения микросервисов.

Основные компоненты:

- Web frontend;
- Backend API;
- PostgreSQL;
- Redis;
- Celery worker;
- Celery beat scheduler;
- OpenSearch;
- Object Storage;
- Nginx Ingress Controller;
- Monitoring stack;
- Logging stack;
- Tracing stack;
- CI/CD pipeline;
- Terraform infrastructure;
- Ansible configuration management.

Упрощённая схема:

```text
Internet
  |
  v
DNS -> HTTPS Load Balancer / Ingress
  |
  v
Nginx Ingress Controller
  |
  v
Kubernetes Services
  |
  +--> Frontend Pods
  |
  +--> Backend Pods
          |
          +--> PostgreSQL
          +--> Redis
          +--> OpenSearch
          +--> Object Storage
```

Структура репозитория

```
recipe-platform/
  backend/
  frontend/
  android/
  desktop/
  infra/
    terraform/
    ansible/
    helm/
    k8s/
  docs/
  scripts/
  .github/
    workflows/
```

### Основные директории

|Директория|Назначение|
|---|---|
|`backend/`|Backend API на FastAPI|
|`frontend/`|Web-приложение на React и TypeScript|
|`android/`|Android-приложение на Kotlin и Jetpack Compose|
|`desktop/`|Desktop-приложение на Tauri|
|`infra/terraform/`|Terraform-код для Yandex Cloud|
|`infra/ansible/`|Ansible-код для настройки Linux VM|
|`infra/helm/`|Helm charts для Kubernetes|
|`infra/k8s/`|Kubernetes-манифесты и шаблоны секретов|
|`docs/`|Проектная и техническая документация|
|`scripts/`|Вспомогательные скрипты|
|`.github/workflows/`|GitHub Actions pipelines|

## Локальный запуск

Локальная среда предназначена для разработки и отладки.

Состав local-окружения:

- backend;
- frontend;
- PostgreSQL;
- Redis;
- OpenSearch;
- MinIO;
- Mailhog (SMTP :1025, Web UI `http://localhost:8025`);
- Celery worker;
- Celery beat scheduler.

Запуск:

```
docker compose up -d
```

Остановка:

```
docker compose down
```

Просмотр логов:

```
docker compose logs -f
```

> Перед первым запуском скопируй `.env.example` в `.env` и заполни переменные.
>
> ```bash
> cp .env.example .env
> docker compose up --build
> ```

## API

Backend предоставляет REST API.

Документация API после запуска backend будет доступна по адресам:

```
/api/docs
/api/openapi.json
```

Основные группы endpoints:

```
/auth
/users
/profiles
/recipes
/categories
/ingredients
/comments
/likes
/favorites
/follows
/meal-plans
/shopping-lists
/admin
/moderation
/notifications
/uploads
/search
```

## CI/CD

CI/CD реализуется через GitHub Actions.

Пайплайны должны выполнять:

- lint;
- unit tests;
- type checks;
- Docker build;
- security scan;
- push Docker images в GHCR;
- deploy в Kubernetes;
- smoke tests;
- rollback при ошибке.

Основные ветки:

|Ветка|Назначение|
|---|---|
|`main`|Production|
|`develop`|Development|
|`feature/*`|Разработка новых функций|
|`release/*`|Подготовка релиза|
|`hotfix/*`|Срочные исправления|

## Docker images

Docker-образы публикуются в GitHub Container Registry.

Пример именования:

```
ghcr.io/<owner>/recipe-backend:<git-sha>
ghcr.io/<owner>/recipe-frontend:<git-sha>
ghcr.io/<owner>/recipe-worker:<git-sha>
```

Для релизов:

```
hcr.io/<owner>/recipe-backend:v1.2.0
ghcr.io/<owner>/recipe-frontend:v1.2.0
ghcr.io/<owner>/recipe-worker:v1.2.0
```

## Kubernetes

Приложение разворачивается в Yandex Managed Kubernetes.

В Kubernetes используются:

- Namespace;
- Deployment;
- Service;
- Ingress;
- ConfigMap;
- Secret;
- ServiceAccount;
- Role / RoleBinding;
- HorizontalPodAutoscaler;
- PodDisruptionBudget;
- NetworkPolicy;
- Job для миграций;
- CronJob;
- readinessProbe;
- livenessProbe.

Деплой выполняется через Helm charts из директории:

```
infra/helm/
```

## Observability

В проекте планируется полный стек наблюдаемости.

### Monitoring

- Prometheus;
- Grafana;
- Alertmanager;
- kube-state-metrics;
- node-exporter;
- blackbox-exporter.

### Logging

- Loki;
- Promtail или Grafana Alloy;
- Grafana.

### Tracing

- OpenTelemetry;
- Tempo или Jaeger.

### Основные алерты

- backend недоступен;
- frontend недоступен;
- высокий процент `5xx`;
- высокая latency;
- pod в `CrashLoopBackOff`;
- node `NotReady`;
- PostgreSQL недоступен;
- Redis недоступен;
- растёт очередь задач;
- истекает TLS-сертификат;
- заканчивается место на диске;
- failed deploy.

## Security

Основные требования безопасности:

- HTTPS;
- хэширование паролей через Argon2 или bcrypt;
- JWT expiration;
- refresh token rotation;
- CORS whitelist;
- rate limiting;
- email verification;
- проверка прав доступа;
- валидация входных данных;
- проверка загружаемых файлов;
- non-root контейнеры;
- минимальные Docker images;
- security scan через Trivy;
- Kubernetes RBAC;
- NetworkPolicy;
- External Secrets Operator;
- хранение секретов вне Git.

Секреты запрещено хранить в репозитории.

## Backup и Disaster Recovery

Планируемые механизмы:

- automated PostgreSQL backups;
- backup retention минимум 7–14 дней;
- проверка восстановления на staging;
- manual backup перед production deploy;
- Object Storage versioning для production;
- Terraform state в remote backend с versioning.

## Критерии готовности

Проект считается завершённым, если:

- приложение доступно по HTTPS-домену;
- работает регистрация и авторизация;
- работает OAuth через Google и Яндекс;
- пользователь может создать рецепт с фото;
- работает поиск;
- работают лайки, комментарии и подписки;
- работает недельный план питания;
- формируется список покупок;
- есть админ-модерация;
- frontend и backend контейнеризованы;
- Docker Compose запускает проект локально;
- Terraform создаёт инфраструктуру в Yandex Cloud;
- Ansible настраивает Linux VM;
- GitHub Actions выполняет CI/CD;
- Docker images публикуются в GHCR;
- приложение развёрнуто в Yandex Managed Kubernetes;
- Nginx Ingress принимает внешний трафик;
- настроен HTTPS;
- настроены мониторинг, логи и алерты;
- есть backup БД;
- секреты вынесены из Git;
- Helm chart находится в репозитории;
- есть smoke tests после деплоя;
- есть возможность rollback.
