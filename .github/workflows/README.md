# GitHub Actions Workflows

GitHub Actions workflows для Recipe Platform.

Директория `.github/workflows/` содержит CI/CD pipeline-файлы, которые автоматизируют проверку кода, тестирование, security scanning, сборку Docker-образов, публикацию в GitHub Container Registry и деплой в Kubernetes через Helm.

## Назначение директории

В `.github/workflows/` находятся YAML-файлы GitHub Actions.

Они отвечают за:

- проверки Pull Request;
- lint backend;
- lint frontend;
- type checks;
- unit tests;
- integration tests;
- Docker build;
- security scan;
- Terraform checks;
- Ansible checks;
- Helm checks;
- сборку Docker images;
- push images в GHCR;
- деплой в dev;
- деплой в staging;
- production deploy с manual approval;
- smoke tests;
- rollback hooks, если будет настроено;
- сборку Android;
- сборку Desktop.

## Рекомендуемая структура workflows

```text
.github/workflows/
  README.md

  pull-request.yml
  deploy-dev.yml
  deploy-staging.yml
  deploy-prod.yml

  terraform.yml
  ansible.yml
  helm.yml

  backend.yml
  frontend.yml
  android.yml
  desktop.yml

  security.yml
```


На начальном этапе workflows можно укрупнить, но по мере роста проекта лучше разделять их по ответственности.

## Основные окружения

Проект использует окружения:

```
local
dev
staging
production
```

GitHub Actions управляет только удалёнными окружениями:

- `dev`;
- `staging`;
- `production`.

`local` запускается разработчиком через Docker Compose.

## Branching strategy

Рекомендуемая стратегия ветвления:

|Ветка|Назначение|
|---|---|
|`main`|Production|
|`develop`|Development|
|`feature/*`|Разработка новых функций|
|`release/*`|Подготовка релиза|
|`hotfix/*`|Срочные исправления|

## Workflow overview

### Pull Request pipeline

Запускается на Pull Request.

Должен выполнять:

- backend lint;
- backend tests;
- backend type checks;
- frontend lint;
- frontend tests;
- frontend type checks;
- Docker build test;
- Terraform format;
- Terraform validate;
- Helm lint;
- Helm template;
- Ansible lint;
- security scan.

Цель — не дать сломать основную ветку.

### Dev deploy pipeline

Запускается после merge в `develop`.

Должен выполнять:

1. 1.tests;
2. 2.Docker build;
3. 3.push images в GHCR;
4. 4.deploy в dev через Helm;
5. 5.migrations;
6. 6.smoke tests.

### Staging deploy pipeline

Запускается для `release/*`.

Должен выполнять:

1. 1.полный набор проверок;
2. 2.сборку release-candidate images;
3. 3.push images в GHCR;
4. 4.deploy в staging;
5. 5.migrations;
6. 6.e2e tests;
7. 7.smoke/load smoke tests.

### Production deploy pipeline

Запускается из `main`.

Должен выполнять:

1. 1.полный набор проверок;
2. 2.сборку production images;
3. 3.push images в GHCR;
4. 4.manual approval;
5. 5.optional pre-deploy backup;
6. 6.deploy в production;
7. 7.migrations;
8. 8.smoke tests;
9. 9.notification;
10. 10.rollback при ошибке, если настроено.

## GitHub Environments

Рекомендуется использовать GitHub Environments:

```
dev
staging
production
```

Для `production` обязательно включить:

- required reviewers;
- manual approval;
- environment secrets;
- deployment protection rules.

Для `staging` желательно включить approval перед релизом.

## Secrets

Секреты хранятся в GitHub Actions Secrets или GitHub Environments Secrets.

Примеры секретов:

```
# YC_SERVICE_ACCOUNT_KEY
## YC_CLOUD_ID
## YC_FOLDER_ID

## KUBE_CONFIG_DEV
## KUBE_CONFIG_STAGING
## KUBE_CONFIG_PROD

## GHCR_TOKEN

## DATABASE_URL_DEV
## DATABASE_URL_STAGING
## DATABASE_URL_PROD

## S3_ACCESS_KEY_ID
## S3_SECRET_ACCESS_KEY

# GOOGLE_OAUTH_CLIENT_SECRET
# YANDEX_OAUTH_CLIENT_SECRET
```

Важно:

- секреты нельзя хранить в Git;
- секреты нельзя печатать в logs;
- для production использовать отдельные environment secrets;
- по возможности использовать короткоживущие credentials;
- IAM-права должны быть минимальными.

## GitHub Container Registry

Docker images публикуются в GitHub Container Registry.

Пример image names:

```
ghcr.io/<owner>/recipe-backend:<git-sha>
ghcr.io/<owner>/recipe-frontend:<git-sha>
ghcr.io/<owner>/recipe-worker:<git-sha>
```

Для релизов:

```
ghcr.io/<owner>/recipe-backend:v1.2.0
ghcr.io/<owner>/recipe-frontend:v1.2.0
ghcr.io/<owner>/recipe-worker:v1.2.0
```

## Image tagging

Рекомендуемые tags:

|Tag|Назначение|
|---|---|
|`<git-sha>`|Уникальная сборка|
|`develop-<git-sha>`|Dev build|
|`staging-<git-sha>`|Staging build|
|`vX.Y.Z`|Release|
|`latest`|Не использовать для production deploy|

Production должен использовать immutable tags:

```
v1.2.0
```

или:

```
<git-sha>
```

Не рекомендуется деплоить production с tag `latest`.

## Pull Request workflow

Пример задач для `pull-request.yml`:

```
name: Pull Request

## on:
  ## pull_request:
    ## branches:
      - develop
      - main

## jobs:
  ## backend:
    name: Backend checks
    runs-on: ubuntu-latest
    ## steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        ## with:
          python-version: "3.12"

      - name: Install backend dependencies
        working-directory: backend
        run: pip install -e ".[dev]"

      - name: Ruff
        working-directory: backend
        run: ruff check .

      - name: Tests
        working-directory: backend
        run: pytest

  ## frontend:
    name: Frontend checks
    runs-on: ubuntu-latest
    ## steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        ## with:
          node-version: "20"

      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci

      - name: Lint
        working-directory: frontend
        run: npm run lint

      - name: Type check
        working-directory: frontend
        run: npm run typecheck

      - name: Tests
        working-directory: frontend
        run: npm run test
```

Это пример, реальный workflow будет расширен.

## Deploy workflow

Типовой deploy через Helm:

```
helm upgrade --install recipe-platform-dev infra/helm/recipe-platform \
  --namespace recipe-platform-dev \
  --create-namespace \
  -f infra/helm/recipe-platform/values.yaml \
  -f infra/helm/recipe-platform/values-dev.yaml \
  --set backend.image.tag=${GITHUB_SHA} \
  --set frontend.image.tag=${GITHUB_SHA} \
  --set worker.image.tag=${GITHUB_SHA}
```

После деплоя запускаются smoke tests:

```
BASE_URL=https://dev.example.com ./scripts/test/smoke-env.sh
```

## Terraform workflow

Terraform workflow должен выполнять:

- `terraform fmt -check`;
- `terraform init`;
- `terraform validate`;
- `terraform plan`;
- manual approval для `apply`;
- отдельные планы для `dev`, `staging`, `prod`.

Применение к production должно быть только вручную.

## Ansible workflow

Ansible workflow должен выполнять:

- YAML lint;
- ansible-lint;
- syntax check.

Пример:

```
ansible-playbook -i infra/ansible/inventories/dev/hosts.yml \
  infra/ansible/playbooks/site.yml \
  --syntax-check
```

Применение Ansible к production — только вручную после approval.

## Helm workflow

Helm workflow должен выполнять:

```
helm lint infra/helm/recipe-platform

helm template recipe-platform-dev infra/helm/recipe-platform \
  -f infra/helm/recipe-platform/values.yaml \
  -f infra/helm/recipe-platform/values-dev.yaml
```

Также желательно проверять staging/prod values:

```
helm template recipe-platform-prod infra/helm/recipe-platform \
  -f infra/helm/recipe-platform/values.yaml \
  -f infra/helm/recipe-platform/values-prod.yaml
```

## Security workflow

Security checks:

- Trivy image scan;
- dependency scan;
- secret scan;
- Dockerfile scan;
- IaC scan;
- npm audit или аналог;
- pip dependency audit;
- Terraform security scan.

Рекомендуемые инструменты:

- Trivy;
- GitHub Dependabot;
- Gitleaks;
- Checkov или tfsec;
- npm audit;
- pip-audit.

## Docker build

Docker build должен выполняться для:

- backend;
- frontend;
- worker, если используется отдельный image;
- scheduler, если используется отдельный image или command.

Пример:

```
docker build -t ghcr.io/<owner>/recipe-backend:${GITHUB_SHA} ./backend
docker build -t ghcr.io/<owner>/recipe-frontend:${GITHUB_SHA} ./frontend
```

Push:

```
docker push ghcr.io/<owner>/recipe-backend:${GITHUB_SHA}
docker push ghcr.io/<owner>/recipe-frontend:${GITHUB_SHA}
```

## Authentication to GHCR

Пример login:

```
- name: Login to GHCR
  uses: docker/login-action@v3
  ## with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

Для push в GHCR нужно выдать permissions:

```
## permissions:
  contents: read
  packages: write
```

## Kubernetes access

Доступ к Kubernetes из GitHub Actions может быть организован через:

- kubeconfig в GitHub Secrets;
- self-hosted runner внутри Yandex Cloud;
- Yandex Cloud CLI + service account;
- OIDC, если будет настроено.

Для production kubeconfig должен быть максимально ограничен.

## Smoke tests

Минимальные smoke tests:

```
## GET /
GET /api/health
GET /api/ready
GET /api/docs
```

Пример запуска:

```
BASE_URL=https://staging.example.com ./scripts/test/smoke-env.sh
```

Smoke tests должны быть обязательным этапом после deploy.

## Rollback

Возможный rollback через Helm:

```
helm rollback recipe-platform-prod <revision> -n recipe-platform-prod
```

Pipeline может выполнять rollback автоматически при ошибке smoke tests, но для production автоматический rollback нужно внедрять осторожно.

Минимально нужно иметь documented manual rollback.

## Android workflow

Android pipeline может выполнять:

- Gradle build;
- lint;
- unit tests;
- debug APK build;
- release build при необходимости.

Пример команд:

```
cd android
./gradlew lint
./gradlew test
./gradlew assembleDebug
```

## Desktop workflow

Desktop pipeline может выполнять:

- install dependencies;
- lint;
- type check;
- tests;
- cargo check;
- cargo clippy;
- Tauri build.

Сборка под разные ОС:

- `ubuntu-latest` для Linux;
- `windows-latest` для Windows.

## Notifications

После deploy можно отправлять уведомления:

- в GitHub summary;
- в Telegram;
- в Slack;
- в email.

Для pet-проекта достаточно GitHub Actions summary, но внешние уведомления будут плюсом.

## Workflow naming

Рекомендуемые имена:

```
Pull Request
Deploy Dev
Deploy Staging
Deploy Production
Terraform
Ansible
Helm
Security
Android
Desktop
```

## Best practices

- использовать pinned action versions;
- не использовать production secrets в PR from forks;
- разделять permissions per job;
- использовать cache для npm/pip/gradle;
- не печатать секреты;
- использовать immutable image tags;
- запускать tests до build/push;
- запускать security scan до deploy;
- требовать approval для production;
- использовать concurrency для deploy workflows;
- хранить deploy history;
- добавлять job summaries.

## Concurrency

Для deploy workflows нужно ограничивать одновременные деплои:

```
## concurrency:
  group: deploy-dev
  cancel-in-progress: true
```

Для production лучше:

```
## concurrency:
  group: deploy-production
  cancel-in-progress: false
```

После создания workflows можно добавить badges в корневой `README.md`

## Production checklist

Перед production deploy pipeline должен подтвердить:

- все тесты прошли;
- Docker images собраны;
- images просканированы;
- staging deploy успешен;
- migrations проверены;
- backup выполнен;
- manual approval получен;
- Helm deploy успешен;
- smoke tests прошли;
- alerts не сработали;
- rollback plan известен.

## Статус

GitHub Actions workflows находятся в разработке.

Приоритет реализации:

1. `pull-request.yml`
2. Backend checks.
3. Frontend checks.
4. Docker build test.
5. Helm lint/template.
6. Terraform fmt/validate.
7. Ansible lint/syntax.
8. Security scan.
9. `deploy-dev.yml`
10. `deploy-staging.yml`
11. `deploy-prod.yml`
12. Android workflow.
13. Desktop workflow.