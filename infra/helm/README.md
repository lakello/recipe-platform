# Helm

Helm charts для развёртывания Recipe Platform в Kubernetes.

Helm используется для шаблонизации Kubernetes-манифестов и управления деплоем приложения в окружения `dev`, `staging` и `production`.

## Назначение директории

В директории `infra/helm/` находятся Helm charts и values-файлы для Kubernetes-деплоя.

Helm отвечает за развёртывание:

- backend API;
- frontend;
- Celery worker;
- Celery beat scheduler;
- migration job;
- ingress;
- services;
- configmaps;
- secrets references;
- service accounts;
- RBAC;
- HPA;
- PodDisruptionBudget;
- NetworkPolicy.

## Что Helm делает в проекте

Helm управляет Kubernetes-ресурсами приложения.

Он отвечает за:

- единый способ деплоя в разные окружения;
- переиспользуемые шаблоны;
- различия между `dev`, `staging` и `production` через values-файлы;
- версионирование релизов;
- rollback;
- установку и обновление приложения.

## Что Helm не делает

Helm не должен:

- создавать Yandex Cloud инфраструктуру;
- создавать Kubernetes cluster;
- создавать Managed PostgreSQL;
- создавать Managed Redis;
- создавать Object Storage buckets;
- настраивать Linux VM;
- собирать Docker images.

Эти задачи выполняются другими инструментами:

| Задача                 | Инструмент                |
| ---------------------- | ------------------------- |
| Cloud infrastructure   | Terraform                 |
| Linux VM configuration | Ansible                   |
| Docker image build     | GitHub Actions            |
| Image registry         | GitHub Container Registry |
| Kubernetes deploy      | Helm                      |
| Runtime orchestration  | Kubernetes                |

## Рекомендуемая структура

```text

infra/helm/

recipe-platform/

Chart.yaml

values.yaml

values-dev.yaml

values-staging.yaml

values-prod.yaml

templates/

_helpers.tpl



backend-deployment.yaml

backend-service.yaml

backend-serviceaccount.yaml

backend-hpa.yaml

backend-pdb.yaml



frontend-deployment.yaml

frontend-service.yaml

frontend-serviceaccount.yaml

frontend-hpa.yaml

frontend-pdb.yaml



worker-deployment.yaml

worker-serviceaccount.yaml

worker-hpa.yaml



scheduler-deployment.yaml

scheduler-serviceaccount.yaml



migration-job.yaml



ingress.yaml

configmap.yaml

secret.yaml

external-secret.yaml

networkpolicy.yaml

rbac.yaml

cronjob.yaml

servicemonitor.yaml



README.md

README.md
```

Основной chart:

```
infra/helm/recipe-platform/
```

## Компоненты приложения

Helm chart должен описывать следующие компоненты.

### Backend

FastAPI backend API.

Kubernetes resources:

- Deployment;
- Service;
- ServiceAccount;
- ConfigMap;
- Secret или ExternalSecret;
- HPA;
- PDB;
- NetworkPolicy;
- ServiceMonitor, если используется Prometheus Operator.

Требования:

- минимум 2 реплики в production;
- rolling update;
- readinessProbe;
- livenessProbe;
- resource requests/limits;
- graceful shutdown;
- запуск от non-root пользователя;
- env из ConfigMap и Secret.

### Frontend

React-приложение, собранное и отдаваемое через Nginx.

Kubernetes resources:

- Deployment;
- Service;
- ServiceAccount;
- HPA;
- PDB;
- NetworkPolicy.

Требования:

- минимум 2 реплики в production;
- readinessProbe;
- livenessProbe;
- Nginx-based image;
- resource requests/limits;
- cache/security headers внутри image.

### Worker

Celery worker для фоновых задач.

Kubernetes resources:

- Deployment;
- ServiceAccount;
- HPA;
- NetworkPolicy.

Фоновые задачи:

- отправка email;
- генерация thumbnails;
- обработка изображений;
- пересчёт списков покупок;
- отправка уведомлений;
- синхронизация поискового индекса.

### Scheduler

Celery beat scheduler для периодических задач.

Kubernetes resources:

- Deployment;
- ServiceAccount;
- NetworkPolicy.

Периодические задачи:

- очистка истёкших токенов;
- пересчёт статистики;
- отправка недельных напоминаний;
- проверка задач модерации.

### Migration Job

Перед обновлением backend должен запускаться Kubernetes Job:

```
alembic upgrade head
```

Job выполняет миграции базы данных.

Требования:

- запуск до выката новой версии приложения;
- доступ к тем же database secrets;
- корректный restartPolicy;
- timeout;
- логирование результата;
- ошибка миграции должна останавливать deploy.

## Values-файлы

### `values.yaml`

Базовые значения по умолчанию.

Содержит общие настройки:

- image names;
- ports;
- probes;
- resources defaults;
- labels;
- common env;
- feature flags.

### `values-dev.yaml`

Настройки dev-окружения:

- меньше replicas;
- меньше resources;
- debug-friendly настройки;
- dev-домены;
- dev secrets references;
- dev namespace;
- возможно отключённые строгие политики.

### `values-staging.yaml`

Настройки staging:

- максимально близко к production;
- отдельные домены;
- отдельные secrets;
- production-like resources;
- включены миграции;
- включены smoke/e2e проверки.

### `values-prod.yaml`

Настройки production:

- минимум 2 реплики для frontend/backend;
- строгие resource limits;
- HPA;
- PDB;
- NetworkPolicy;
- production secrets;
- production domains;
- TLS;
- monitoring;
- strict securityContext.

## Пример values

``` yaml
## global:

environment: dev

imagePullSecrets: []



## backend:

enabled: true

replicaCount: 1

## image:

repository: ghcr.io/example/recipe-backend

tag: latest

pullPolicy: IfNotPresent

## service:

port: 8000

## resources:

## requests:

cpu: 100m

memory: 256Mi

## limits:

cpu: 500m

memory: 512Mi



## frontend:

enabled: true

replicaCount: 1

## image:

repository: ghcr.io/example/recipe-frontend

tag: latest

pullPolicy: IfNotPresent

## service:

port: 80



## worker:

enabled: true

replicaCount: 1

## image:

repository: ghcr.io/example/recipe-worker

tag: latest

pullPolicy: IfNotPresent



## ingress:

enabled: true

className: nginx

## hosts:

- host: dev.example.com

## paths:

- path: /

### service: frontend

- path: /api

service: backend

## tls:

enabled: true

secretName: recipe-platform-dev-tls
```

## Image tags

Docker images публикуются в GitHub Container Registry.

Пример:

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

В CI/CD image tag должен передаваться в Helm через:

``` bash
--set backend.image.tag=${GITHUB_SHA}

--set frontend.image.tag=${GITHUB_SHA}

--set worker.image.tag=${GITHUB_SHA}
```

## Namespaces

Рекомендуемые namespaces:

```
recipe-platform-dev
recipe-platform-staging
recipe-platform-prod
```

Создание namespace может быть:

- частью Helm chart;
- отдельным bootstrap manifest;
- частью CI/CD;
- частью Terraform/Kubernetes provider.

Главное — обеспечить изоляцию окружений.

## Ingress

Для входящего HTTPS-трафика используется Nginx Ingress Controller.

Ingress должен маршрутизировать:

- frontend;
- backend API;
- опционально admin frontend, если будет выделен;
- health endpoints, если нужно.

Пример маршрутизации:

```
https://dev.example.com/       -> frontend service
https://dev.example.com/api    -> backend service
```

Или отдельный API-домен:

```
https://api.dev.example.com    -> backend service
```

## TLS

HTTPS обеспечивается через:

- cert-manager;
- Let's Encrypt ClusterIssuer;
- Kubernetes TLS secrets.

Ingress должен иметь аннотации cert-manager.

Пример:

```
cert-manager.io/cluster-issuer: letsencrypt-prod
```

Также нужно включить redirect HTTP -> HTTPS.

## ConfigMap и Secrets

### ConfigMap

Хранит несекретные настройки:

- `APP_ENV`;
- `API_PREFIX`;
- `LOG_LEVEL`;
- `CORS_ALLOWED_ORIGINS`;
- `S3_BUCKET_NAME`;
- `OPENSEARCH_URL`;
- feature flags.

### Secrets

Хранят чувствительные данные:

- database password;
- Redis password;
- JWT secret;
- OAuth client secrets;
- S3 credentials;
- SMTP credentials.

Рекомендуемый подход:

- секреты хранятся в Yandex Lockbox;
- External Secrets Operator синхронизирует их в Kubernetes Secrets;
- Helm ссылается на уже созданные Kubernetes Secrets.

Секреты нельзя хранить в values-файлах в Git.

## External Secrets

Если используется External Secrets Operator, chart может включать `ExternalSecret`.

Примерная идея:

``` yaml
apiVersion: external-secrets.io/v1beta1

kind: ExternalSecret

## metadata:

name: recipe-platform-backend

## spec:

refreshInterval: 1h

## secretStoreRef:

name: yandex-lockbox

kind: ClusterSecretStore

## target:

name: recipe-platform-backend

## data:

- secretKey: DATABASE_URL

## remoteRef:

key: backend-database-url
```

## Probes

### Backend

``` yaml
## readinessProbe:

## httpGet:

path: /ready

port: 8000



## livenessProbe:

## httpGet:

path: /health

port: 8000
```

Frontend

``` yaml

## readinessProbe:

## httpGet:

path: /health

port: 80



## livenessProbe:

## httpGet:

path: /health

port: 80
```

Probes обязательны для production-like Kubernetes деплоя.

## Resources

Каждый workload должен иметь resource requests и limits.

Пример:

``` yaml
## resources:

## requests:

cpu: 100m

memory: 256Mi

## limits:

cpu: 500m

memory: 512Mi
```

Для production значения подбираются после наблюдений и нагрузочного тестирования.

## HPA

HorizontalPodAutoscaler используется для масштабирования.

Пример:

``` yaml
## autoscaling:

enabled: true

minReplicas: 2

maxReplicas: 10

targetCPUUtilizationPercentage: 70
```

Для worker можно позже добавить масштабирование по длине очереди через KEDA.

## PodDisruptionBudget

PDB нужен, чтобы при maintenance или node drain не упали все реплики.

Пример:

``` yaml
## podDisruptionBudget:

enabled: true

minAvailable: 1
```

В production PDB должен быть включён для frontend и backend.

## NetworkPolicy

NetworkPolicy ограничивает сетевые взаимодействия внутри Kubernetes.

Примерные правила:

- ingress может обращаться к frontend/backend;
- backend может обращаться к PostgreSQL, Redis, OpenSearch, Object Storage;
- frontend не должен напрямую обращаться к PostgreSQL/Redis;
- worker может обращаться к PostgreSQL, Redis, Object Storage, OpenSearch;
- monitoring может scrape metrics endpoints;
- deny by default там, где возможно.

## SecurityContext

Workloads должны запускаться с безопасными настройками.

Пример:

``` yaml
## securityContext:

runAsNonRoot: true

readOnlyRootFilesystem: true

allowPrivilegeEscalation: false

## capabilities:

## drop:

- ALL
```

Настройки нужно адаптировать под конкретные images.

## RBAC

Для каждого компонента желательно использовать отдельный ServiceAccount.

Принципы:

- минимальные права;
- не использовать default service account;
- не выдавать cluster-admin;
- Role/RoleBinding вместо ClusterRole там, где возможно.

## ServiceMonitor

Если используется Prometheus Operator, можно добавить ServiceMonitor для backend metrics.

Backend должен отдавать endpoint:

```
/metrics
```

ServiceMonitor позволит Prometheus автоматически находить target.

## Установка chart

Перейти в директорию chart:

```
cd infra/helm/recipe-platform
```

Установить dev-релиз:

``` bash
helm upgrade --install recipe-platform-dev . \

--namespace recipe-platform-dev \

--create-namespace \

-f values.yaml \

-f values-dev.yaml
```

Установить staging-релиз:

``` bash
helm upgrade --install recipe-platform-staging . \

--namespace recipe-platform-staging \

--create-namespace \

-f values.yaml \

-f values-staging.yaml
```

Установить production-релиз:

``` bash
helm upgrade --install recipe-platform-prod . \

--namespace recipe-platform-prod \

--create-namespace \

-f values.yaml \

-f values-prod.yaml
```

Передача image tag

``` bash
helm upgrade --install recipe-platform-dev . \

--namespace recipe-platform-dev \

-f values.yaml \

-f values-dev.yaml \

--set backend.image.tag=${GITHUB_SHA} \

--set frontend.image.tag=${GITHUB_SHA} \

--set worker.image.tag=${GITHUB_SHA}
```

## Проверка шаблонов

Render templates локально:

``` bash
helm template recipe-platform-dev . \

-f values.yaml \

-f values-dev.yaml
```

Проверка chart:

```
helm lint .
```

Dry run:

``` bash
helm upgrade --install recipe-platform-dev . \

--namespace recipe-platform-dev \

-f values.yaml \

-f values-dev.yaml \

--dry-run \

--debug
```

## Rollback

Посмотреть историю релиза:

```
helm history recipe-platform-dev -n recipe-platform-dev
```

Откатиться на предыдущую ревизию:

```
helm rollback recipe-platform-dev 1 -n recipe-platform-dev
```

Для production rollback должен быть частью аварийной процедуры.

## Helm в CI/CD

GitHub Actions pipeline должен выполнять:

- `helm lint`;
- `helm template`;
- деплой в dev после merge в `develop`;
- деплой в staging из `release/*`;
- production deploy из `main` после manual approval;
- smoke tests после деплоя;
- rollback при ошибке, если настроено.

Пример команды deploy:

``` bash
helm upgrade --install recipe-platform-dev infra/helm/recipe-platform \

--namespace recipe-platform-dev \

--create-namespace \

-f infra/helm/recipe-platform/values.yaml \

-f infra/helm/recipe-platform/values-dev.yaml \

--set backend.image.tag=${GITHUB_SHA} \

--set frontend.image.tag=${GITHUB_SHA} \

--set worker.image.tag=${GITHUB_SHA}
```

## Smoke tests после deploy

Минимальные проверки:

``` bash
curl -f https://dev.example.com/

curl -f https://dev.example.com/api/health

curl -f https://dev.example.com/api/ready
```

Дополнительно:

- проверить `/api/docs`;
- проверить login endpoint;
- проверить список рецептов;
- проверить frontend SPA fallback;
- проверить отсутствие 5xx на ingress.

## Зависимости кластера

Перед установкой chart в Kubernetes должны быть установлены:

- Nginx Ingress Controller;
- cert-manager;
- External Secrets Operator;
- monitoring stack, если ServiceMonitor включён;
- logging stack;
- storage/network policies, если используются.

Эти компоненты могут устанавливаться отдельными Helm charts или bootstrap-процессом.

## Production checklist

Перед production deploy проверить:

- image tags не `latest`;
- secrets существуют;
- migrations протестированы на staging;
- backup БД выполнен;
- readiness/liveness probes настроены;
- resources заданы;
- HPA включён;
- PDB включён;
- NetworkPolicy включены;
- TLS работает;
- ingress корректно маршрутизирует;
- smoke tests готовы;
- rollback procedure известна;
- monitoring и alerts активны.

## Безопасность

Основные требования:

- не хранить secrets в Git;
- не использовать `latest` tag в production;
- запускать containers от non-root;
- задавать resource limits;
- использовать отдельные ServiceAccounts;
- ограничивать RBAC;
- включать NetworkPolicy;
- включать securityContext;
- использовать imagePullPolicy осознанно;
- не давать privileged mode;
- не монтировать Docker socket;
- не раскрывать debug endpoints публично.

## Статус

Helm charts находятся в разработке.

Приоритет реализации:

1. 1.Базовый chart `recipe-platform`.
2. 2.Backend Deployment/Service.
3. 3.Frontend Deployment/Service.
4. 4.Worker Deployment.
5. 5.Scheduler Deployment.
6. 6.ConfigMap.
7. 7.Secrets references / ExternalSecret.
8. 8.Ingress.
9. 9.Migration Job.
10. 10.Probes.
11. 11.Resources.
12. 12.HPA.
13. 13.PDB.
14. 14.NetworkPolicy.
15. 15.ServiceMonitor.
16. 16.CI/CD integration.
