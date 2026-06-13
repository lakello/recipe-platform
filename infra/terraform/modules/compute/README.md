# Модуль compute

Terraform-модуль для создания Compute instance (bastion host / self-hosted GitHub Actions runner) в Yandex Cloud.

## Что создаёт модуль

- `yandex_vpc_address` — статический публичный IP, закреплённый за VM
- `yandex_vpc_security_group` — security group с правилом: SSH (порт 22) разрешён только с указанного CIDR
- `yandex_compute_instance` — VM на платформе `standard-v3`, Ubuntu 24.04 LTS, размещается в public subnet

## Назначение

VM выполняет две роли:

- **Bastion host** — единственная точка SSH-входа в инфраструктуру
- **Self-hosted runner** — выполнение задач GitHub Actions с доступом к приватной сети (настраивается Ansible)

Terraform отвечает только за создание VM и сетевые настройки. Установка пакетов, hardening и настройка runner — задача Ansible.

## Использование

```hcl
module "compute" {
  source = "../../modules/compute"

  subnet_id        = module.network.public_subnet_id
  network_id       = module.network.vpc_id
  image_id         = data.yandex_compute_image.ubuntu.id
  ssh_public_key   = var.ssh_public_key
  allowed_ssh_cidr = var.allowed_ssh_cidr
}
```

## Переменные

| Переменная        | Тип    | По умолчанию      | Описание                                      |
|-------------------|--------|-------------------|-----------------------------------------------|
| `zone`            | string | `ru-central1-a`   | Зона доступности                              |
| `network_id`      | string | —                 | ID VPC сети                                   |
| `subnet_id`       | string | —                 | ID публичной подсети                          |
| `image_id`        | string | —                 | ID образа ОС (рекомендуется из data source)   |
| `ssh_user`        | string | `ubuntu`          | Имя пользователя для SSH                      |
| `ssh_public_key`  | string | —                 | Публичный SSH-ключ                            |
| `allowed_ssh_cidr`| string | —                 | CIDR разрешённого IP для SSH (`x.x.x.x/32`)  |

## Outputs

| Output        | Описание                                    |
|---------------|---------------------------------------------|
| `instance_id` | ID созданного инстанса                      |
| `public_ip`   | Статический публичный IP (для Ansible)      |
| `internal_ip` | Внутренний IP инстанса                      |

## Структура

```
modules/compute/
  main.tf        # yandex_vpc_address, yandex_vpc_security_group, yandex_compute_instance
  variables.tf   # входные переменные
  outputs.tf     # instance_id, public_ip, internal_ip
  providers.tf   # required_providers
```
