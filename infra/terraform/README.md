# Terraform Infrastructure

Terraform-код для создания и управления облачной инфраструктурой Recipe Platform в Yandex Cloud.

Terraform отвечает за декларативное описание инфраструктуры: сети, Kubernetes-кластера, managed-баз данных, Object Storage, DNS, service accounts, IAM-доступов и вспомогательных виртуальных машин.

## Назначение директории

В директории `infra/terraform/` находится Infrastructure as Code для Yandex Cloud.

Terraform используется для создания:

- VPC network;
- public/private subnets;
- route tables;
- NAT gateway;
- security groups;
- Yandex Managed Kubernetes;
- Kubernetes node groups;
- Yandex Managed PostgreSQL;
- Yandex Managed Redis;
- Object Storage buckets;
- service accounts;
- IAM permissions;
- DNS-записей;
- static IP;
- Compute instance для bastion/self-hosted runner;
- Lockbox secrets;
- remote backend для Terraform state.

## Что Terraform делает в проекте

Terraform отвечает только за создание и изменение cloud-ресурсов.

Terraform не должен:

- устанавливать Docker внутри VM;
- настраивать пользователей Linux;
- править `sshd_config`;
- устанавливать GitHub Actions runner;
- выполнять hardening операционной системы;
- деплоить приложение в Kubernetes.

Эти задачи выполняют другие части проекта:

| Задача                           | Инструмент            |
| -------------------------------- | --------------------- |
| Создание cloud-инфраструктуры    | Terraform             |
| Настройка Linux внутри VM        | Ansible               |
| Сборка и тестирование приложения | GitHub Actions        |
| Деплой приложения в Kubernetes   | Helm / GitHub Actions |
| Запуск приложения                | Kubernetes            |

## Yandex Cloud

Основное облако проекта:

```text
Yandex Cloud
```

Планируемые сервисы:

- Yandex VPC;
- Yandex Managed Kubernetes;
- Yandex Managed PostgreSQL;
- Yandex Managed Redis;
- Yandex Object Storage;
- Yandex DNS;
- Yandex Certificate Manager, если потребуется;
- Yandex Lockbox;
- Yandex Compute Cloud;
- Yandex Monitoring;
- Yandex Cloud Logging.

## Окружения

Terraform должен поддерживать несколько окружений:

```
dev
staging
prod
```

Окружение `local` не создаётся Terraform — оно запускается через Docker Compose.

### Dev

Используется для автоматического деплоя из ветки `develop`.

Особенности:

- минимальные ресурсы;
- отдельная БД;
- отдельный bucket;
- отдельные secrets;
- отдельный Kubernetes namespace;
- можно использовать preemptible nodes, если подходит.

### Staging

Production-like окружение для проверки релизов.

Особенности:

- максимально похоже на production;
- отдельная БД;
- отдельный bucket;
- отдельные secrets;
- проверка миграций;
- нагрузочные smoke tests;
- деплой из `release/*`.

### Production

Публичное стабильное окружение.

Особенности:

- manual approval перед изменениями;
- backup;
- monitoring;
- alerting;
- autoscaling;
- strict security;
- отдельные secrets;
- ограниченный доступ;
- осторожное применение Terraform изменений.

## Рекомендуемая структура

```
infra/terraform/
  envs/
    dev/
      backend.tf
      providers.tf
      main.tf
      variables.tf
      outputs.tf
      terraform.tfvars.example
    staging/
      backend.tf
      providers.tf
      main.tf
      variables.tf
      outputs.tf
      terraform.tfvars.example
    prod/
      backend.tf
      providers.tf
      main.tf
      variables.tf
      outputs.tf
      terraform.tfvars.example
  modules/
    network/
      main.tf
      variables.tf
      outputs.tf
    kubernetes/
      main.tf
      variables.tf
      outputs.tf
    postgres/
      main.tf
      variables.tf
      outputs.tf
    redis/
      main.tf
      variables.tf
      outputs.tf
    object-storage/
      main.tf
      variables.tf
      outputs.tf
    compute/
      main.tf
      variables.tf
      outputs.tf
    dns/
      main.tf
      variables.tf
      outputs.tf
    lockbox/
      main.tf
      variables.tf
      outputs.tf
  README.md
```

## Сетевая архитектура

Terraform создаёт сетевую основу проекта.

Компоненты:

- VPC network;
- public subnet;
- private subnet;
- route table;
- NAT gateway;
- security groups.

### Public subnet

Используется для:

- external load balancer;
- bastion host;
- NAT gateway;
- публичных точек входа.

### Private subnet

Используется для:

- Kubernetes worker nodes;
- PostgreSQL;
- Redis;
- внутренних сервисов.

### Базовая схема

```
Internet
  |
  v
DNS -> HTTPS Load Balancer / Ingress
  |
  v
Public Subnet
  |
  v
Nginx Ingress Controller
  |
  v
Private Subnet
  |
  +--> Kubernetes Worker Nodes
  +--> Managed PostgreSQL
  +--> Managed Redis
```

## Security Groups

Доступ должен быть ограничен по принципу минимальных прав.

Примерные правила:

### Ingress

- разрешить `80/443` из Internet к Load Balancer / Ingress;
- разрешить SSH только к bastion host и только с доверенных IP;
- запретить прямой доступ к PostgreSQL из Internet;
- запретить прямой доступ к Redis из Internet.

### Internal

- Kubernetes nodes могут обращаться к PostgreSQL;
- Kubernetes nodes могут обращаться к Redis;
- bastion может администрировать private resources при необходимости;
- monitoring может собирать метрики с разрешённых targets.

## Managed Kubernetes

Terraform создаёт Yandex Managed Kubernetes cluster.

Требования:

- control plane управляется Yandex Cloud;
- worker nodes размещаются в private subnet;
- отдельные node groups для разных типов нагрузки;
- IAM service accounts с минимальными правами;
- cluster endpoint должен быть защищён;
- production должен иметь надёжную node group конфигурацию.

### Node groups

Рекомендуемые node groups:

|Node group|Назначение|
|---|---|
|`system`|ingress, monitoring, system workloads|
|`app`|backend, frontend, worker|
|`spot` / `preemptible`|dev/staging workloads, если подходит|

Для production preemptible nodes нужно использовать осторожно.

## PostgreSQL

Terraform создаёт Yandex Managed PostgreSQL.

PostgreSQL хранит:

- пользователей;
- профили;
- рецепты;
- ингредиенты;
- комментарии;
- лайки;
- избранное;
- подписки;
- планы питания;
- списки покупок;
- роли;
- аудит;
- модерацию.

Требования:

- отдельные базы или кластеры для dev/staging/prod;
- automated backups;
- backup retention минимум 7–14 дней;
- доступ только из Kubernetes security group;
- отдельные пользователи БД;
- TLS при необходимости;
- production backup должен быть включён обязательно.

## Redis

Terraform создаёт Yandex Managed Redis.

Redis используется для:

- кэширования популярных рецептов;
- rate limiting;
- Celery broker;
- временных OAuth-данных;
- временных токенов;
- очередей фоновых задач.

Требования:

- доступ только из Kubernetes;
- пароль хранится в secret manager;
- production должен иметь настройки надёжности согласно возможностям сервиса.

## Object Storage

Terraform создаёт buckets.

Примерные buckets:

```
recipe-platform-dev
recipe-platform-staging
recipe-platform-prod
recipe-platform-tfstate
```

Object Storage используется для:

- фотографий рецептов;
- аватаров пользователей;
- thumbnails;
- экспортированных списков покупок;
- backup exports;
- Terraform state.

Требования:

- запрет публичной записи;
- доступ через signed URLs;
- IAM-доступ с минимальными правами;
- lifecycle rules;
- versioning для production bucket;
- versioning для Terraform state bucket.

## Terraform State

Terraform state должен храниться удалённо.

Рекомендуемый backend:

```
Yandex Object Storage
```

Требования:

- отдельный bucket для state;
- versioning включён;
- публичный доступ запрещён;
- доступ ограничен IAM;
- state не хранится в Git;
- секреты не должны попадать в outputs.

Пример `backend.tf`:

``` hci
terraform {

backend "s3" {

bucket = "recipe-platform-tfstate"

key = "dev/terraform.tfstate"

region = "ru-central1"



endpoint = "storage.yandexcloud.net"

skip_region_validation = true

skip_credentials_validation = true

}

}
```

## DNS и HTTPS

Terraform может создавать DNS-записи в Yandex DNS.

Пример доменов:

```
dev.example.com
staging.example.com
example.com
api.example.com
grafana.example.com
```

HTTPS обычно настраивается в Kubernetes через:

- Nginx Ingress Controller;
- cert-manager;
- Let's Encrypt ClusterIssuer.

Terraform может создать:

- DNS zone;
- A/CNAME records;
- static IP;
- managed certificate, если выбран подход через Yandex Certificate Manager.

## Lockbox

Yandex Lockbox используется для хранения секретов.

Примеры секретов:

- database password;
- Redis password;
- JWT secret;
- OAuth client secrets;
- S3 credentials;
- SMTP credentials.

Terraform может создавать secret containers, но значения секретов нужно передавать осторожно.

Важно:

- не коммитить секреты в `.tfvars`;
- не выводить секреты в `outputs`;
- ограничить доступ к Lockbox через IAM;
- использовать External Secrets Operator для доставки секретов в Kubernetes.

## Bastion / Self-hosted Runner

Terraform может создать Compute instance для:

- bastion host;
- self-hosted GitHub Actions runner.

Terraform отвечает за:

- создание VM;
- сетевые интерфейсы;
- security group;
- service account;
- metadata;
- SSH key injection.

Ansible отвечает за:

- установку пакетов;
- настройку пользователей;
- hardening;
- установку Docker;
- настройку GitHub runner;
- настройку firewall;
- установку node exporter.

## Переменные

Пример переменных:

``` hcl

variable "cloud_id" {

type = string

description = "Yandex Cloud ID"

}



variable "folder_id" {

type = string

description = "Yandex Cloud Folder ID"

}



variable "environment" {

type = string

description = "Environment name: dev, staging, prod"

}



variable "zone" {

type = string

description = "Yandex Cloud zone"

default = "ru-central1-a"

}



variable "domain_name" {

type = string

description = "Base domain name"

}

```

## tfvars

Для каждого окружения должен быть пример файла:

```
terraform.tfvars.example
```

Пример:

```
cloud_id = "your-cloud-id"

folder_id = "your-folder-id"

environment = "dev"

zone = "ru-central1-a"

domain_name = "example.com"
```

Реальный файл:

```
terraform.tfvars
```

не должен попадать в Git.

Добавить в `.gitignore`:

```
*.tfvars
!*.tfvars.example
.terraform/
terraform.tfstate
terraform.tfstate.*
```

## Базовые команды

Перейти в окружение:

```
cd infra/terraform/envs/dev
```

Инициализация:

```
terraform init
```

Проверка форматирования:

```
terraform fmt -recursive
```

Валидация:

```
terraform validate
```

План изменений:

```
terraform plan
```

Применение:

```
terraform apply
```

Удаление окружения:

```
terraform destroy
```

> `terraform destroy` для production использовать крайне осторожно.

## Работа с окружениями

Пример для dev:

``` bash
cd infra/terraform/envs/dev

terraform init

terraform plan

terraform apply
```

Пример для staging:

``` bash
cd infra/terraform/envs/staging

terraform init

terraform plan

terraform apply
```

Пример для production:

``` bash
cd infra/terraform/envs/prod

terraform init

terraform plan

terraform apply
```

Для production изменения должны выполняться только после review и approval.

## CI/CD для Terraform

Terraform должен проверяться в GitHub Actions.

На Pull Request:

- `terraform fmt -check`;
- `terraform validate`;
- `terraform plan`;
- комментирование plan в PR, если будет настроено.

Для apply:

- dev может применяться автоматически после merge;
- staging — после approval или из release pipeline;
- production — только manual approval.

## Безопасность

Основные требования:

- не хранить секреты в Git;
- не выводить секреты в outputs;
- использовать remote state;
- включить versioning для state bucket;
- ограничить IAM-доступ;
- использовать service accounts с минимальными правами;
- ограничить SSH доступ к bastion;
- закрыть PostgreSQL и Redis от Internet;
- разделять dev/staging/prod;
- проверять Terraform plan перед apply;
- использовать отдельные credentials для CI.

## Naming convention

Рекомендуемый формат имён ресурсов:

```
recipe-platform-<env>-<resource>
```

Примеры:

```
recipe-platform-dev-vpc
recipe-platform-dev-k8s
recipe-platform-dev-postgres
recipe-platform-dev-redis
recipe-platform-dev-bucket
recipe-platform-prod-k8s
```

## Tags / Labels

Все ресурсы должны иметь labels:

```
labels = {

project = "recipe-platform"

environment = var.environment

managed_by = "terraform"

}
```

## Outputs

Terraform outputs должны отдавать только несекретную информацию:

- Kubernetes cluster id;
- VPC id;
- subnet ids;
- bucket names;
- public IP;
- DNS names.

Нельзя выводить:

- database passwords;
- Redis passwords;
- JWT secrets;
- OAuth secrets;
- private keys.

## Порядок реализации

Рекомендуемый порядок:

1. 1.Remote state bucket.
2. 2.Provider configuration.
3. 3.Network module.
4. 4.Security groups.
5. 5.Object Storage buckets.
6. 6.PostgreSQL.
7. 7.Redis.
8. 8.Kubernetes cluster.
9. 9.Node groups.
10. 10.Bastion/self-hosted runner VM.
11. 11.DNS records.
12. 12.Lockbox secrets.
13. 13.Outputs для Ansible и CI/CD.

## Статус

Terraform-инфраструктура находится в разработке.

Приоритет:

1. 1.Yandex Cloud provider.
2. 2.Remote state.
3. 3.Network.
4. 4.Security groups.
5. 5.Managed Kubernetes.
6. 6.Managed PostgreSQL.
7. 7.Managed Redis.
8. 8.Object Storage.
9. 9.Bastion/self-hosted runner.
10. 10.DNS.
11. 11.Lockbox.
12. 12.Terraform CI pipeline.
