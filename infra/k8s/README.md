# infra/k8s

Kubernetes-манифесты и шаблоны секретов для Recipe Platform.

## Назначение

Директория `infra/k8s/` содержит вспомогательные Kubernetes-манифесты, которые не входят в Helm chart: ручные секреты, примеры конфигурации и заготовки для начального деплоя.

Основной деплой в Kubernetes выполняется через Helm chart из `infra/helm/`.

## Состав

- `oauth-secrets.example.yaml` — шаблон Kubernetes Secret для OAuth-credentials (Google и Яндекс); значения пустые, файл предназначен для заполнения и применения вручную.
- `secrets/` — директория для реальных секретов; **не коммитить заполненные файлы в Git**.
  - `oauth.yaml` — Kubernetes Secret для OAuth (значения пусты, используется как шаблон).

## Связи с проектом

OAuth credentials, определённые в этих секретах, передаются в backend-контейнер через переменные окружения:

```
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
YANDEX_CLIENT_ID
YANDEX_CLIENT_SECRET
```

Backend использует их в `app/services/oauth.py` и `app/api/oauth.py`.

Для локальной разработки те же переменные задаются в `.env` (корень проекта) и передаются через `docker-compose.yml`.

## Текущий статус

Kubernetes-инфраструктура не развёрнута. Файлы — заготовки для будущего деплоя.

Реализовано:
- Шаблон Secret для OAuth credentials.

Планируется:
- Полный деплой через Helm chart (`infra/helm/`).
- Namespace, Deployment, Service, Ingress, ConfigMap, HPA, NetworkPolicy.
- Secrets через External Secrets Operator (Yandex Lockbox).
- Kubernetes Job для Alembic-миграций.

## Важно для разработки

Никогда не коммитить заполненные Secret-файлы с реальными credentials в Git.

Для production использовать External Secrets Operator или Sealed Secrets вместо хранения секретов в репозитории.

Применить шаблон вручную (заполнив значения):

```bash
kubectl apply -f infra/k8s/secrets/oauth.yaml
```
