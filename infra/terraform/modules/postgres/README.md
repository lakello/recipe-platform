# Модуль postgres

Terraform-модуль для создания Yandex Managed PostgreSQL кластера с базой данных и пользователем приложения.

## Ресурсы

| Ресурс | Описание |
|---|---|
| `yandex_mdb_postgresql_cluster` | Managed PostgreSQL кластер |
| `yandex_mdb_postgresql_database` | База данных приложения |
| `yandex_mdb_postgresql_user` | Пользователь приложения |

## Конфигурация кластера

- PostgreSQL 15, `s2.micro`, 16 ГБ `network-ssd`
- Backup window: 03:00, retention 7 дней
- Maintenance window: суббота 12:00
- `environment`: `PRODUCTION` для prod, `PRESTABLE` для остальных
- `deletion_protection`: включён автоматически для prod

## Безопасность

Кластер принимает подключения только от ресурсов, входящих в переданную security group (`database_sg` — порт 5432 разрешён только из приватной подсети Kubernetes).

## Переменные

| Переменная | Описание |
|---|---|
| `cluster_name` | Имя кластера |
| `environment` | Окружение (dev / staging / prod) |
| `folder_id` | ID папки Yandex Cloud |
| `network_id` | ID VPC |
| `subnet_id` | ID подсети (приватная) |
| `security_group_ids` | Security groups кластера |
| `database_name` | Имя базы данных |
| `database_user` | Имя пользователя БД |
| `database_password` | Пароль пользователя (sensitive) |
| `zone` | Зона доступности хоста |

## Outputs

| Output | Описание |
|---|---|
| `cluster_id` | ID кластера |
| `fqdn` | FQDN хоста кластера |
| `db_name` | Имя базы данных |
| `db_user` | Имя пользователя (без пароля) |
