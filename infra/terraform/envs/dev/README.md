# Окружение dev

Terraform-конфигурация для окружения `dev`. Используется для автоматического деплоя из ветки `develop`.

## Структура

```
envs/dev/
  providers.tf              # Yandex Cloud provider (yandex-cloud/yandex ~> 0.206)
  backend.tf                # S3 remote backend (Yandex Object Storage)
  backend.hcl.example       # шаблон credentials для backend (не коммитится)
  main.tf                   # подключение модулей
  variables.tf              # входные переменные окружения
  outputs.tf                # outputs окружения
  terraform.tfvars.example  # пример значений переменных
  terraform.tfvars          # реальные значения (не коммитится)
  Makefile                  # команды init/plan/apply/destroy/fmt/validate
  authorized_key.json       # ключ сервисного аккаунта (не коммитится)
```

## Подключённые модули

| Модуль    | Назначение                                      |
|-----------|-------------------------------------------------|
| `network` | VPC, subnets, NAT gateway, security groups      |

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
