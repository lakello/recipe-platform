# Contributing

Спасибо за интерес к проекту Recipe Platform.

Этот проект использует production-like DevOps-подход: код, инфраструктура, Kubernetes-манифесты, Helm charts, CI/CD workflows и документация версионируются в Git и проходят через Pull Request review.

## Git branching strategy

В проекте используется Git Flow-подобная стратегия ветвления.

Основные ветки:

- `main` — production-ветка
- `develop` — development-ветка
- `feature/*` — ветки для новых функций
- `release/*` — ветки подготовки релиза
- `hotfix/*` — ветки срочных исправлений production

## Назначение веток

### `main`

Ветка `main` содержит только стабильный production-ready код.
Из этой ветки выполняется деплой в production-окружение.

Правила:

- прямые push в `main` запрещены;
- изменения попадают только через Pull Request;
- merge разрешён только из `release/*` или `hotfix/*`;
- перед merge должны пройти CI-проверки;
- production deploy требует manual approval;
- каждый production-релиз должен иметь Git tag.

Пример тега:

```text
v1.2.0
```
---
### `develop`

Ветка `develop` используется для интеграции текущей разработки.

Из этой ветки выполняется автоматический деплой в dev-окружение.

Правила:

- прямые push в `develop` запрещены;
- изменения попадают через Pull Request из `feature/*`;
- после merge в `develop` запускается CI/CD pipeline;
- успешный merge может автоматически деплоиться в dev namespace Kubernetes;
- ветка должна оставаться рабочей и пригодной для интеграционного тестирования.

### `feature/*`

Ветки `feature/*` используются для разработки новых функций, улучшений и обычных задач.

Создаются от ветки `develop`.

Формат имени:

```
feature/<short-description>
```

Примеры:
```
feature/auth-email-login
feature/oauth-yandex
feature/recipe-photo-upload
feature/shopping-list-generation
```

Правила:

- создаются только от `develop`;
- вливаются только в `develop`;
- должны проходить lint, tests, type checks и security checks;
- одна ветка должна решать одну логическую задачу;
- перед созданием PR желательно обновить ветку от актуальной `develop`.

Пример:
``` bash
git checkout develop
git pull origin develop
git checkout -b feature/recipe-comments
```
---
### `release/*`

Ветки `release/*` используются для подготовки релиза.

Создаются от `develop`, когда набор изменений готов к стабилизации перед production.

Формат имени:

```
release/<version>
```

Примеры:
```
release/1.0.0
release/1.1.0
release/2.0.0
```
Назначение:

- финальное тестирование;
- деплой в staging;
- проверка миграций;
- исправление release-blocker багов;
- обновление версии;
- подготовка changelog;
- smoke/e2e/load checks перед production.

Правила:

- создаются от `develop`;
- автоматически или вручную деплоятся в staging;
- в `release/*` разрешены только bugfix, документация и release-related изменения;
- после проверки ветка вливается в `main`;
- после merge в `main` создаётся Git tag;
- изменения из `release/*` также должны быть возвращены в `develop`.

Пример процесса:
``` bash
git checkout develop
git pull origin develop
git checkout -b release/1.2.0
```

После успешной проверки:

```
release/1.2.0 -> main
release/1.2.0 -> develop
```

---

### `hotfix/*`

Ветки `hotfix/*` используются для срочных исправлений production.

Создаются от `main`.

Формат имени:

```
hotfix/<short-description>
```

Рекомендуемый формат с версией:

```
hotfix/1.2.1-critical-login-fix
```

Примеры:

```
hotfix/fix-jwt-refresh
hotfix/fix-paymentless-production-config
hotfix/fix-ingress-tls
```

Правила:

- создаются только от `main`;
- используются только для критичных production-исправлений;
- после проверки вливаются в `main`;
- после merge в `main` создаётся patch tag;
- изменения обязательно вливаются обратно в `develop`;
- при необходимости также вливаются в активную `release/*` ветку.

Пример:

``` bash
git checkout main
git pull origin main
git checkout -b hotfix/fix-refresh-token-rotation
```

После исправления:

```
hotfix/* -> main
hotfix/* -> develop
hotfix/* -> release/*, если активный релиз существует
```

## Deployment mapping

Соответствие веток и окружений:

|Branch|Environment|Deploy|
|---|---|---|
|`feature/*`|no automatic deploy|CI checks only|
|`develop`|`dev`|automatic deploy|
|`release/*`|`staging`|automatic or manual deploy|
|`main`|`production`|manual approval|
|`hotfix/*`|`production` after merge to `main`|manual approval|

## Pull Request rules

Все изменения должны проходить через Pull Request.

Минимальные требования к PR:

- понятное название;
- описание изменений;
- ссылка на задачу, если есть;
- список затронутых компонентов;
- результаты локальной проверки, если применимо;
- отсутствие секретов в коде;
- успешное прохождение CI.

Пример хорошего названия PR:

```
feat(auth): add email login endpoint
fix(recipe): prevent duplicate likes
infra(terraform): add redis security group
ci: add staging deploy workflow
docs: add branching rules
```

## Required checks

Для Pull Request должны проходить проверки:

- backend lint;
- backend tests;
- frontend lint;
- frontend tests;
- type checks;
- Docker build test;
- security scan;
- Terraform format/validate для инфраструктурных изменений;
- Helm template/lint для Kubernetes/Helm изменений.

## Commit message convention

Рекомендуется использовать Conventional Commits.

Формат:

```
<type>(scope): <description>
```

Типы:

- `feat` — новая функциональность;
- `fix` — исправление ошибки;
- `docs` — документация;
- `style` — форматирование без изменения логики;
- `refactor` — рефакторинг;
- `test` — тесты;
- `chore` — служебные изменения;
- `ci` — CI/CD;
- `infra` — инфраструктура;
- `build` — сборка и зависимости.

Примеры:

```
feat(auth): add google oauth callback
fix(recipes): validate uploaded image mime type
docs: add contributing guide
infra(terraform): add managed redis module
ci: add pull request workflow
```

## Versioning

Для production-релизов используется Semantic Versioning.

Формат:

```
## MAJOR.MINOR.PATCH
```

Примеры:

```
v1.0.0
v1.1.0
v1.1.1
```

Правила:

- `MAJOR` — несовместимые изменения API или архитектуры;
- `MINOR` — новая функциональность без нарушения совместимости;
- `PATCH` — исправления ошибок и hotfix.

## Secrets policy

Секреты запрещено хранить в Git.

Нельзя коммитить:

- пароли;
- JWT secret;
- OAuth client secrets;
- database credentials;
- Redis password;
- S3/Object Storage keys;
- SMTP credentials;
- kubeconfig;
- Terraform credentials;
- `.env` с реальными значениями.

Для секретов используются:

- GitHub Actions Secrets;
- Yandex Lockbox;
- Kubernetes Secrets;
- External Secrets Operator;
- локальные `.env` файлы, исключённые через `.gitignore`.

## Recommended local workflow

``` bash
git checkout develop

git pull origin develop

  

git checkout -b feature/my-task

  

# make changes

git add .

git commit -m "feat(scope): describe change"

  

git push origin feature/my-task
```

После этого нужно создать Pull Request в `develop`.

## Branch cleanup

После merge Pull Request ветку нужно удалить:
``` bash
git branch -d feature/my-task

git push origin --delete feature/my-task
```

