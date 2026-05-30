# Documentation

Документация Recipe Platform.

В директории `docs/` хранится проектная, техническая, инфраструктурная и эксплуатационная документация. Эта директория нужна, чтобы проект был понятен не только во время разработки, но и при демонстрации в портфолио, ревью архитектуры, эксплуатации и восстановлении после инцидентов.

## Назначение директории

`docs/` содержит документацию по:

- продукту;
- архитектуре;
- API;
- базе данных;
- инфраструктуре;
- Kubernetes;
- CI/CD;
- security;
- observability;
- backup и restore;
- runbooks;
- troubleshooting;
- development workflow;
- окружениям;
- решениям и компромиссам.

## Для кого эта документация

Документация предназначена для:

- разработчиков backend;
- разработчиков frontend;
- DevOps-инженеров;
- QA;
- администраторов;
- ревьюеров проекта;
- будущего владельца проекта;
- самого автора проекта как база знаний.

## Рекомендуемая структура

```text

docs/

README.md

  

product/

overview.md

roles.md

features.md

user-flows.md

  

architecture/

overview.md

system-context.md

components.md

networking.md

environments.md

decisions/

adr-0001-architecture-style.md

adr-0002-cloud-provider.md

adr-0003-kubernetes-deployment.md

  

api/

overview.md

auth.md

recipes.md

meal-plans.md

shopping-lists.md

moderation.md

  

database/

overview.md

schema.md

migrations.md

backup-restore.md

  

infrastructure/

terraform.md

ansible.md

yandex-cloud.md

dns-tls.md

object-storage.md

  

kubernetes/

overview.md

helm.md

ingress.md

secrets.md

network-policies.md

scaling.md

rollback.md

  

ci-cd/

overview.md

branching-strategy.md

github-actions.md

release-process.md

  

observability/

overview.md

metrics.md

logs.md

tracing.md

alerts.md

dashboards.md

  

security/

overview.md

secrets.md

auth.md

container-security.md

kubernetes-security.md

hardening.md

  

operations/

runbooks/

backend-down.md

database-unavailable.md

redis-unavailable.md

high-5xx-rate.md

failed-deploy.md

certificate-expiring.md

troubleshooting.md

incident-response.md

  

development/

local-setup.md

coding-standards.md

testing.md

docker-compose.md

  

diagrams/

architecture.drawio

network.drawio

deployment.drawio
```

Структура может расширяться по мере роста проекта.

## Основные разделы

## Product

Документация продукта описывает, что делает Recipe Platform.

### Что должно быть описано

- назначение продукта;
- целевая аудитория;
- роли пользователей;
- основные пользовательские сценарии;
- функциональные требования;
- нефункциональные требования.

### Ключевые роли

- гость;
- пользователь;
- автор;
- модератор;
- администратор.

### Основные функции

- регистрация и авторизация;
- OAuth через Google и Яндекс;
- рецепты;
- категории;
- фотографии;
- поиск;
- лайки;
- избранное;
- комментарии;
- подписки;
- план питания;
- список покупок;
- уведомления;
- жалобы;
- модерация;
- админ-панель.

## Architecture

Архитектурная документация описывает устройство системы.

### Что должно быть описано

- общий обзор архитектуры;
- системный контекст;
- основные компоненты;
- взаимодействие компонентов;
- сетевой поток;
- окружения;
- границы ответственности;
- технические компромиссы.

### Рекомендуемый стиль

Проект строится как модульный монолит с возможностью дальнейшего выделения микросервисов.

Компоненты:

- Web frontend;
- Android client;
- Desktop client;
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

## ADR

Для важных архитектурных решений рекомендуется использовать ADR — Architecture Decision Records.

Пример структуры ADR:

```
# ADR-0001: Использование модульного монолита

## Статус

Accepted

## Контекст

Нужно выбрать архитектурный стиль backend-приложения.

## Решение

Использовать модульный монолит на FastAPI.

## Последствия

## Плюсы:
- проще разработка;
- проще тестирование;
- проще деплой;
- можно выделить микросервисы позже.

## Минусы:
- нужна дисциплина в границах модулей;
- при росте проекта может потребоваться разделение.
```

Рекомендуемые ADR:

- выбор FastAPI;
- выбор React;
- выбор Yandex Cloud;
- выбор Terraform;
- выбор Ansible;
- выбор Kubernetes;
- выбор Helm;
- выбор PostgreSQL;
- выбор Redis;
- выбор OpenSearch;
- выбор Tauri;
- выбор observability stack.

## API documentation

API-документация должна дополнять OpenAPI.

OpenAPI доступен из backend:

```
/api/docs
/api/openapi.json
```

В `docs/api/` стоит хранить:

- описание auth flow;
- описание OAuth flow;
- правила работы с JWT;
- описание refresh token rotation;
- примеры запросов;
- примеры ошибок;
- соглашения по статус-кодам;
- pagination;
- filtering;
- sorting;
- rate limiting;
- versioning API.

## Database documentation

Документация базы данных должна описывать:

- основные сущности;
- связи;
- миграции;
- индексы;
- backup/restore;
- soft delete;
- audit logs;
- требования к данным.

Минимальные таблицы:

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

## Infrastructure documentation

Инфраструктурная документация описывает Yandex Cloud и IaC.

Что нужно описать:

- Terraform structure;
- remote state;
- VPC;
- subnets;
- NAT;
- security groups;
- Managed Kubernetes;
- Managed PostgreSQL;
- Managed Redis;
- Object Storage;
- DNS;
- Lockbox;
- bastion;
- self-hosted runner;
- IAM.

## Kubernetes documentation

Документация Kubernetes должна описывать:

- namespaces;
- Helm chart;
- Deployments;
- Services;
- Ingress;
- ConfigMaps;
- Secrets;
- External Secrets;
- ServiceAccounts;
- RBAC;
- HPA;
- PDB;
- NetworkPolicy;
- migration jobs;
- rollback;
- production checklist.

## CI/CD documentation

CI/CD документация должна описывать:

- GitHub Actions workflows;
- branching strategy;
- pull request pipeline;
- deploy dev pipeline;
- deploy staging pipeline;
- deploy production pipeline;
- manual approval;
- Docker image tagging;
- GHCR;
- smoke tests;
- rollback;
- release process.

Рекомендуемая стратегия ветвления:

```
main        -> production
develop     -> development
feature/*   -> feature branches
release/*   -> release candidates
hotfix/*    -> urgent fixes
```

## Observability documentation

Observability-документация описывает мониторинг, логи, трейсы и алерты.

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

### Alerts

Документировать нужно:

- условия срабатывания;
- severity;
- получателей;
- runbook link;
- expected action.

Примеры алертов:

- backend down;
- frontend down;
- высокий процент 5xx;
- высокая latency;
- pod crashloop;
- node not ready;
- PostgreSQL недоступен;
- Redis недоступен;
- очередь задач растёт;
- истекает TLS-сертификат;
- заканчивается место;
- failed deploy.

## Security documentation

Security-документация должна описывать:

- модель угроз на базовом уровне;
- работу с секретами;
- authentication;
- authorization;
- password hashing;
- JWT;
- refresh token rotation;
- CORS;
- rate limiting;
- загрузку файлов;
- container security;
- Kubernetes security;
- RBAC;
- NetworkPolicy;
- Linux hardening;
- incident response.

Важно зафиксировать:

```
Секреты запрещено хранить в Git.
```

## Operations and Runbooks

Runbooks описывают, что делать при авариях.

Примеры runbooks:

### Backend down

- проверить Ingress;
- проверить Service;
- проверить Pods;
- посмотреть logs;
- проверить readiness/liveness;
- проверить последние deploy events;
- при необходимости выполнить rollback.

### Database unavailable

- проверить Managed PostgreSQL status;
- проверить network/security groups;
- проверить database credentials;
- проверить connection pool;
- проверить alerts Yandex Cloud;
- при необходимости переключиться на restore-процедуру.

### Failed deploy

- проверить GitHub Actions logs;
- проверить Helm release status;
- проверить migration job;
- проверить events в namespace;
- выполнить Helm rollback;
- создать incident note.

## Development documentation

Документация разработки должна описывать:

- как поднять проект локально;
- как настроить backend;
- как настроить frontend;
- как запустить тесты;
- как работать с Docker Compose;
- как создавать миграции;
- как писать feature branches;
- code style;
- commit style;
- pull request checklist.

## Diagrams

В `docs/diagrams/` можно хранить диаграммы:

- system context;
- container diagram;
- network diagram;
- Kubernetes deployment diagram;
- CI/CD pipeline diagram;
- database ERD.

Форматы:

- `.drawio`;
- `.png`;
- `.svg`;
- `.mmd` для Mermaid.

Пример Mermaid-диаграммы:

```
flowchart TD
    User[User] --> DNS[DNS]
    DNS --> Ingress[Nginx Ingress]
    Ingress --> Frontend[Frontend]
    Ingress --> Backend[Backend API]
    Backend --> PostgreSQL[(PostgreSQL)]
    Backend --> Redis[(Redis)]
    Backend --> S3[(Object Storage)]
    Backend --> OpenSearch[(OpenSearch)]
```

## Правила ведения документации

Документация должна быть:

- актуальной;
- краткой там, где это возможно;
- конкретной;
- связанной с кодом и инфраструктурой;
- полезной для запуска и эксплуатации;
- без секретов;
- с примерами команд;
- с указанием окружений;
- с описанием причин решений.

## Что нельзя хранить в docs

В документации нельзя хранить:

- реальные пароли;
- private keys;
- access tokens;
- refresh tokens;
- OAuth client secrets;
- production database URLs с паролями;
- закрытые credentials;
- персональные данные пользователей.

Для примеров использовать placeholders:

```
<database-password>
<oauth-client-secret>
<bucket-name>
<cloud-id>
<folder-id>
```

## Шаблон документа

Рекомендуемый шаблон для новых документов:

```
# Название документа

  

## Назначение

  

Кратко описать, для чего нужен документ.

  

## Контекст

  

Почему тема важна для проекта.

  

## Детали

  

Основное содержание.

  

## Команды

  

Если применимо, добавить команды.

  

## Security notes

  

Если применимо, описать требования безопасности.

  

## Related documents

  

Ссылки на связанные документы.
```

Шаблон runbook

```
# Runbook: Название инцидента

## Симптомы

Что видно при проблеме.

## Возможные причины

Список вероятных причин.

## Диагностика

Команды и проверки.

## Решение

Пошаговые действия.

## Rollback

Как откатиться.

## Escalation

Кого уведомить или что проверить дальше.

## Postmortem

Что зафиксировать после инцидента.
```

## Статус

Документация находится в разработке.

Приоритет наполнения:

1. 1.Product overview.
2. 2.Architecture overview.
3. 3.Local setup.
4. 4.Backend API overview.
5. 5.Infrastructure overview.
6. 6.Terraform guide.
7. 7.Kubernetes/Helm guide.
8. 8.CI/CD guide.
9. 9.Security overview.
10. 10.Observability overview.
11. 11.Backup/restore.
12. 12.Runbooks.