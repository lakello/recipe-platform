# Окружение dev

Terraform-конфигурация для окружения `dev`. Используется для автоматического деплоя из ветки `develop`.

## Структура

```
envs/dev/
  providers.tf              # Yandex Cloud provider (yandex-cloud/yandex ~> 0.206)
  backend.tf                # S3 remote backend (Yandex Object Storage)
  backend.hcl.example       # шаблон credentials для backend (не коммитится)
  data.tf                   # data sources (yandex_compute_image для bastion)
  main.tf                   # подключение модулей
  variables.tf              # входные переменные окружения
  outputs.tf                # outputs окружения
  terraform.tfvars.example  # пример значений переменных
  terraform.tfvars          # реальные значения (не коммитится)
  Makefile                  # команды init/plan/apply/destroy/fmt/validate
  authorized_key.json       # ключ сервисного аккаунта (не коммитится)
```

## Подключённые модули

| Модуль           | Назначение                                                   |
|------------------|--------------------------------------------------------------|
| `network`        | VPC, subnets, NAT gateway, security groups                   |
| `kubernetes`     | Managed Kubernetes cluster, node groups system и app         |
| `postgres`       | Managed PostgreSQL кластер, БД и пользователь приложения     |
| `redis`          | Managed Redis кластер с паролем и ограничением доступа       |
| `object_storage` | Object Storage bucket, service account, IAM, static keys     |
| `compute`        | Bastion/self-hosted runner VM, static IP, security group     |

## Команды

```bash
make init     # terraform init -backend-config=backend.hcl
make plan     # fmt + validate + terraform plan
make apply    # terraform apply
make destroy  # terraform destroy
make fmt      # terraform fmt -recursive
make validate # terraform validate
make clean    # удалить .terraform/ и *.tfplan
make help     # список команд
```

## Переменные

| Переменная            | Описание                            |
|-----------------------|-------------------------------------|
| `cloud_id`            | ID облака в Yandex Cloud            |
| `folder_id`           | ID папки в Yandex Cloud             |
| `environment`         | Название окружения                  |
| `instance_tags`       | Labels для ресурсов                 |
| `availability_zones`  | Зоны доступности                    |
| `public_subnet_cidr`  | CIDR публичной подсети              |
| `private_subnet_cidr` | CIDR приватной подсети              |
| `k8s_version`         | Версия Kubernetes                   |
| `database_name`       | Имя базы данных PostgreSQL          |
| `database_user`       | Имя пользователя БД                 |
| `database_password`   | Пароль пользователя БД (sensitive)  |
| `redis_password`      | Пароль доступа к Redis (sensitive)  |
| `service_access_id`   | Access key ID для S3 API (Object Storage) |
| `service_access_key`  | Secret key для S3 API (sensitive)   |
| `alloved_ssh_cidr`    | CIDR вашего IP для доступа к bastion по SSH (например, `1.2.3.4/32`) |
| `ssh_public_key`      | Публичный SSH-ключ для авторизации на bastion |
