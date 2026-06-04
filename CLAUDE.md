# CLAUDE.md

Этот файл содержит инструкции для Claude Code (claude.ai/code) при работе с данным репозиторием.

## Обзор проекта

Recipe Platform — полноценное приложение с DevOps-подходом. Компоненты: бэкенд на FastAPI, фронтенд на React/TypeScript, десктопное приложение на Tauri, Android-приложение на Kotlin/Jetpack Compose, инфраструктура в Yandex Cloud (Terraform + Ansible + Kubernetes/Helm).

**Статус**: предреализационный этап. Все директории содержат только README-файлы; код ещё не написан.

## Локальная разработка

Полный стек запускается через Docker Compose из корня проекта (бэкенд, фронтенд, Postgres, Redis, OpenSearch, MinIO, Mailhog, Celery worker + beat).

Файл `.env.example` ещё не создан — при начале реализации создавать `.env` файлы (они в `.gitignore`).

## Команды сборки и тестирования

### Бэкенд (Python 3.12, FastAPI)
```bash
cd backend
ruff check .                                           # линтинг
ruff format .                                          # форматирование
mypy app                                               # проверка типов
pytest                                                 # тесты
alembic upgrade head                                   # применить миграции (перед запуском сервера)
uvicorn app.main:app --reload                          # dev-сервер
alembic revision --autogenerate -m "describe change"  # создать миграцию
```

### Фронтенд (React, TypeScript, Vite)
```bash
cd frontend
npm run lint        # линтинг (ESLint)
npm run typecheck   # проверка типов
npm run test        # тесты (Vitest)
npm run dev         # dev-сервер
npm run build       # production-сборка
```

### Инфраструктура
```bash
cd infra/terraform && terraform fmt && terraform validate
cd infra/helm && helm lint . && helm template .
ansible-lint        # линтинг Ansible-плейбуков
```

## Git-воркфлоу

Полная стратегия ветвления и правила PR описаны в `CONTRIBUTING.md`.

Ключевые правила:
- Прямые пуши в `main` и `develop` запрещены
- `feature/*` — создаётся от `develop`, вливается в `develop`
- `release/*` — создаётся от `develop`, вливается в `main`, затем обратно в `develop`
- `hotfix/*` — создаётся от `main`, вливается в `main` + `develop` + активный `release/*`
- PR требует прохождения всех CI-проверок; деплой в production требует ручного подтверждения
- После merge ветку нужно удалить (`git branch -d` + `git push origin --delete`)

## Формат коммитов

Conventional Commits: `<type>(scope): <description>`

Типы: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `infra`, `build`

```
feat(auth): add google oauth callback
fix(recipes): validate uploaded image mime type
infra(terraform): add managed redis module
ci: add pull request workflow
```

## Политика секретов

Никогда не коммитить секреты. Запрещено: пароли, JWT-секреты, OAuth-credentials, DB/Redis/S3/SMTP-учётные данные, kubeconfig, Terraform-credentials, `.env`-файлы с реальными значениями.

Использовать: GitHub Actions Secrets, Yandex Lockbox, Kubernetes Secrets, External Secrets Operator или локальные `.env` (в `.gitignore`).

## Тегирование Docker-образов

Production-образы должны использовать иммутабельные теги (git SHA или semver — например, `v1.2.0`, `sha-abc1234`). Тег `latest` в production запрещён.

## Требования к PR

Заголовок PR — в формате Conventional Commits. Описание должно включать: суть изменений, ссылку на задачу (если есть), затронутые компоненты, отсутствие секретов. Все CI-проверки должны пройти до merge.

## Процесс выполнения задач

Пользователь учится — задачи выполняются **совместно, пошагово**. Строгий порядок:

1. **Объяснить** — Claude объясняет текущий шаг: что нужно сделать и почему.
2. **Выполнить** — пользователь выполняет шаг самостоятельно.
3. **Проверить** — Claude проверяет результат (читает файлы, запрашивает вывод команд и т.д.).
4. **Исправить или продолжить** — если есть ошибки или рекомендации, сначала разбираемся с ними (возврат к п. 2), и только после подтверждения что всё корректно — переходим к следующему шагу.

Правила:
- Никогда не пропускать шаги и не переходить вперёд без явного подтверждения текущего.
- Если пользователь не понимает что-то — объяснять простым языком, без лишнего жаргона.
- Проверку выполнять инструментами (Read, Bash), а не на слово.
- Если шаг сложный — разбить его на подшаги.
- **Git-операции (коммиты, ветки, stash) выполняет Claude**, а не пользователь. Соблюдать стратегию ветвления из `CONTRIBUTING.md`: feature-ветки создаются от `develop`, коммиты — в формате Conventional Commits. При отсутствии `.pre-commit-config.yaml` использовать `PRE_COMMIT_ALLOW_NO_CONFIG=1`.
