# Инфраструктура

Инфраструктурный код и конфигурация Recipe Platform.

## Назначение

Директория `infra/` содержит весь Infrastructure as Code и конфигурацию для развёртывания и управления проектом: облачную инфраструктуру, Kubernetes-деплой, настройку серверов и CI/CD-артефакты.

## Состав

- `terraform/` — Infrastructure as Code для Yandex Cloud. Создаёт сети, Kubernetes-кластер, базы данных, Object Storage, DNS и вспомогательные VM.
- `ansible/` — Configuration management для Linux VM. Настраивает bastion host, hardening, Docker, GitHub Actions runner, node exporter.
- `helm/` — Helm charts для развёртывания приложения в Kubernetes.
- `k8s/` — Вспомогательные Kubernetes-манифесты, не входящие в Helm chart (шаблоны секретов, заготовки для ручного применения).

## Связи с проектом

Инструменты работают в связке:

| Задача | Инструмент |
|---|---|
| Создание cloud-инфраструктуры | Terraform (`infra/terraform/`) |
| Настройка Linux VM | Ansible (`infra/ansible/`) |
| Сборка Docker images | GitHub Actions (`.github/workflows/`) |
| Деплой приложения в Kubernetes | Helm (`infra/helm/`) |
| Запуск приложения | Kubernetes |

## Текущий статус

| Компонент | Статус |
|---|---|
| `terraform/` — модули и окружение dev | ✅ Реализовано |
| `terraform/` — окружения staging и prod | 🚧 В работе (базовая структура) |
| `ansible/` | ⏳ Планируется |
| `helm/` | ⏳ Планируется |
| `k8s/` | 🚧 Частично (шаблоны секретов) |

## Важно для разработки

- Никогда не коммитить секреты: `terraform.tfvars`, `authorized_key.json`, `backend.hcl`, `kubeconfig`, заполненные Secret-файлы.
- Terraform-состояние хранится в Yandex Object Storage (remote backend), а не локально.
- Порядок применения инфраструктуры: Terraform → Ansible → Helm.
