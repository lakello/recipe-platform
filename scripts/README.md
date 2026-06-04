# Scripts

Вспомогательные скрипты Recipe Platform.

Директория `scripts/` предназначена для хранения небольших автоматизаций, которые упрощают разработку, локальный запуск, проверки, деплой, диагностику и эксплуатационные задачи.

## Назначение директории

В `scripts/` хранятся shell/python-скрипты для повторяемых операций:

- локальная разработка;
- запуск и остановка окружения;
- проверки качества кода;
- тестирование;
- генерация файлов;
- работа с Docker;
- работа с Kubernetes;
- smoke tests;
- backup/restore helper scripts;
- диагностика;
- maintenance-задачи.

Скрипты не должны заменять Terraform, Ansible, Helm или GitHub Actions, но могут быть удобной оболочкой над часто используемыми командами.

## Что можно хранить в scripts

Примеры допустимых скриптов:

```text
scripts/
  README.md

  dev/
    up.sh
    down.sh
    logs.sh
    reset-local-db.sh
    seed-local-data.sh

  test/
    lint-all.sh
    test-all.sh
    smoke-local.sh
    smoke-env.sh

  docker/
    build-backend.sh
    build-frontend.sh
    build-all.sh
    push-images.sh

  k8s/
    kube-context.sh
    port-forward-backend.sh
    port-forward-grafana.sh
    describe-failed-pods.sh
    get-events.sh

  db/
    backup-postgres.sh
    restore-postgres.sh
    migrate.sh

  ops/
    check-health.sh
    check-cert.sh
    collect-diagnostics.sh

  utils/
    generate-jwt-secret.sh
    wait-for-url.sh
```

Структура может быть изменена по мере развития проекта.

## Что не нужно хранить в scripts

В `scripts/` не должны попадать:

- секреты;
- private keys;
- production passwords;
- токены доступа;
- большие бинарные файлы;
- одноразовые локальные файлы;
- state-файлы Terraform;
- kubeconfig с production-доступом;
- дампы production-БД.

## Принципы написания скриптов

Скрипты должны быть:

- понятными;
- идемпотентными, где это возможно;
- безопасными по умолчанию;
- с проверкой ошибок;
- с понятным выводом;
- с help-сообщением, если есть аргументы;
- совместимыми с Linux;
- пригодными для запуска локально и в CI, если нужно.

Для shell-скриптов рекомендуется использовать:

```
set -euo pipefail
```

Пример:

```
#!/usr/bin/env bash

set -euo pipefail

echo "Running checks..."
```

## Права на выполнение

Shell-скрипты должны иметь executable permissions:

```
chmod +x scripts/dev/up.sh
```

Проверить:

```
ls -la scripts/dev/up.sh
```

## Переменные окружения

Скрипты могут использовать переменные окружения.

Пример:

```
APP_ENV="${APP_ENV:-local}"
NAMESPACE="${NAMESPACE:-recipe-platform-dev}"
```

Но секреты нельзя хардкодить внутри скриптов.

Допустимо читать секреты из:

- переменных окружения;
- GitHub Actions Secrets;
- Yandex Lockbox;
- `.env` файлов, которые не попадают в Git.

## Пример `.env`

Для локальной разработки можно использовать `.env` в корне проекта.

Пример:

```
APP_ENV=local
COMPOSE_PROJECT_NAME=recipe-platform
```

Файлы с реальными секретами должны быть добавлены в `.gitignore`.

## Dev scripts

Скрипты для локальной разработки.

### `scripts/dev/up.sh`

Запуск local-окружения:

```
#!/usr/bin/env bash

set -euo pipefail

docker compose up -d
```

Использование:

```
./scripts/dev/up.sh
```

### `scripts/dev/down.sh`

Остановка local-окружения:

```
#!/usr/bin/env bash

set -euo pipefail

docker compose down
```

Использование:

```
./scripts/dev/down.sh
```

### `scripts/dev/logs.sh`

Просмотр логов:

```
#!/usr/bin/env bash

set -euo pipefail

## SERVICE="${1:-}"

if [[ -z "$SERVICE" ]]; then
  docker compose logs -f
else
  docker compose logs -f "$SERVICE"
fi
```

Использование:

```
./scripts/dev/logs.sh
./scripts/dev/logs.sh backend
```

## Test scripts

Скрипты для проверок и тестов.

### `scripts/test/lint-all.sh`

Запуск lint для backend и frontend:

```
#!/usr/bin/env bash

set -euo pipefail

echo "Lint backend..."
cd backend
ruff check .
cd ..

echo "Lint frontend..."
cd frontend
npm run lint
cd ..
```

### `scripts/test/test-all.sh`

Запуск тестов:

```
#!/usr/bin/env bash

set -euo pipefail

echo "Test backend..."
cd backend
pytest
cd ..

echo "Test frontend..."
cd frontend
npm run test
cd ..
```

## Docker scripts

Скрипты для сборки Docker images.

### `scripts/docker/build-backend.sh`

```
#!/usr/bin/env bash

set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-local}"

docker build \
  -t "recipe-backend:${IMAGE_TAG}" \
  ./backend
```

scripts/docker/build-frontend.sh

```
#!/usr/bin/env bash

set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-local}"

docker build \
  -t "recipe-frontend:${IMAGE_TAG}" \
  ./frontend
```

scripts/docker/build-all.sh

```
#!/usr/bin/env bash

set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-local}"

IMAGE_TAG="$IMAGE_TAG" ./scripts/docker/build-backend.sh
IMAGE_TAG="$IMAGE_TAG" ./scripts/docker/build-frontend.sh
```

Использование:

```
IMAGE_TAG=dev ./scripts/docker/build-all.sh
```

## Kubernetes scripts

Скрипты для диагностики Kubernetes.

### `scripts/k8s/describe-failed-pods.sh`

Идея скрипта:

```
#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-recipe-platform-dev}"

kubectl get pods -n "$NAMESPACE"

echo "Failed pods:"
kubectl get pods -n "$NAMESPACE" \
  --field-selector=status.phase!=Running,status.phase!=Succeeded || true
```

scripts/k8s/get-events.sh

```
#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-recipe-platform-dev}"

kubectl get events -n "$NAMESPACE" --sort-by=.lastTimestamp
```

scripts/k8s/port-forward-grafana.sh

```
#!/usr/bin/env bash

set -euo pipefail

NAMESPACE="${NAMESPACE:-monitoring}"
SERVICE="${SERVICE:-grafana}"

kubectl port-forward -n "$NAMESPACE" svc/"$SERVICE" 3000:80
```

## Database scripts

Скрипты для локальной или эксплуатационной работы с БД.

### `scripts/db/migrate.sh`

```
#!/usr/bin/env bash

set -euo pipefail

cd backend
alembic upgrade head
```

### Backup

Backup production-БД должен выполняться осторожно.

Скрипт backup не должен содержать пароль в коде.

Примерный подход:

```
#!/usr/bin/env bash

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"

pg_dump "$DATABASE_URL" > "$BACKUP_DIR/postgres-$TIMESTAMP.sql"
```

Использование:

```
DATABASE_URL="postgresql://..." ./scripts/db/backup-postgres.sh
```

> Для production предпочтительно использовать managed backups Yandex Managed PostgreSQL и отдельную restore-процедуру.

## Smoke tests

Smoke tests используются после деплоя.

### `scripts/test/smoke-env.sh`

Пример:

```
#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${BASE_URL:?BASE_URL is required}"

echo "Checking frontend..."
curl -fsS "$BASE_URL/" > /dev/null

echo "Checking backend health..."
curl -fsS "$BASE_URL/api/health" > /dev/null

echo "Checking backend readiness..."
curl -fsS "$BASE_URL/api/ready" > /dev/null

echo "Smoke tests passed"
```

Использование:

```
BASE_URL=https://dev.example.com ./scripts/test/smoke-env.sh
```

## Ops scripts

Скрипты для эксплуатации и диагностики.

### `scripts/ops/check-health.sh`

Проверка health endpoints:

```
#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${BASE_URL:?BASE_URL is required}"

curl -fsS "$BASE_URL/api/health"
curl -fsS "$BASE_URL/api/ready"
```

### `scripts/ops/check-cert.sh`

Проверка TLS-сертификата:

```
#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:?DOMAIN is required}"

echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null \
  | openssl x509 -noout -dates
```

Использование:

```
DOMAIN=example.com ./scripts/ops/check-cert.sh
```

## Utils

### `scripts/utils/generate-jwt-secret.sh`

Генерация JWT secret:

```
#!/usr/bin/env bash

set -euo pipefail

openssl rand -base64 64
```

Использование:

```
./scripts/utils/generate-jwt-secret.sh
```

Сгенерированное значение нужно сохранить в secret manager, например Yandex Lockbox, а не в Git.

## Проверка shell-скриптов

Рекомендуется использовать:

- ShellCheck;
- shfmt.

Проверить:

```
shellcheck scripts/**/*.sh
```

Форматировать:

```
shfmt -w scripts
```

## Использование в CI/CD

Некоторые скрипты могут вызываться из GitHub Actions.

Примеры:

```
./scripts/test/lint-all.sh
./scripts/test/test-all.sh
BASE_URL=https://dev.example.com ./scripts/test/smoke-env.sh
```

Требования для CI:

- скрипты должны завершаться с non-zero exit code при ошибке;
- вывод должен быть понятным;
- секреты не должны печататься в logs;
- команды должны быть воспроизводимыми.

## Безопасность

Основные правила:

- не хардкодить секреты;
- не печатать секреты в stdout/stderr;
- использовать `set -euo pipefail`;
- проверять обязательные переменные окружения;
- использовать dry-run для опасных операций;
- для production требовать явного подтверждения;
- не запускать destructive-команды без защиты.

Пример защиты для production:

```
if [[ "${APP_ENV:-}" == "production" ]]; then
  echo "You are running this script against production."
  read -r -p "Type 'production' to continue: " CONFIRM

  if [[ "$CONFIRM" != "production" ]]; then
    echo "Aborted"
    exit 1
  fi
fi
```

## Именование

Рекомендуемые правила:

- использовать kebab-case;
- расширение `.sh` для shell-скриптов;
- понятные имена;
- группировать по директориям.

Примеры:

```
reset-local-db.sh
seed-local-data.sh
smoke-env.sh
check-cert.sh
collect-diagnostics.sh
```

## Статус

Скрипты будут добавляться по мере развития проекта.

Приоритет:

1. 1.`dev/up.sh`
2. 2.`dev/down.sh`
3. 3.`dev/logs.sh`
4. 4.`test/lint-all.sh`
5. 5.`test/test-all.sh`
6. 6.`docker/build-backend.sh`
7. 7.`docker/build-frontend.sh`
8. 8.`docker/build-all.sh`
9. 9.`test/smoke-env.sh`
10. 10.`k8s/get-events.sh`
11. 11.`k8s/describe-failed-pods.sh`
12. 12.`ops/check-cert.sh`
13. 13.`utils/generate-jwt-secret.sh`
