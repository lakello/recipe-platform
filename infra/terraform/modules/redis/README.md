# Модуль redis

Terraform-модуль для создания Yandex Managed Redis кластера.

## Ресурсы

| Ресурс | Описание |
|---|---|
| `yandex_mdb_redis_cluster` | Managed Redis кластер |

## Конфигурация кластера

- Redis 6.2, `hm1.nano`, 16 ГБ `network-ssd`
- Политика вытеснения: `ALLKEYS_LRU`
- Persistence: `ON` для prod, `OFF` для остальных окружений
- `environment`: `PRODUCTION` для prod, `PRESTABLE` для остальных
- `deletion_protection`: включён автоматически для prod

## Безопасность

Кластер принимает подключения только от ресурсов, входящих в переданную security group (`database_sg` — порт 6379 разрешён только из приватной подсети Kubernetes). Публичный доступ отсутствует.

## Переменные

| Переменная | Описание |
|---|---|
| `cluster_name` | Имя кластера |
| `environment` | Окружение (dev / staging / prod) |
| `network_id` | ID VPC |
| `subnet_id` | ID подсети (приватная) |
| `security_group_ids` | Security groups кластера |
| `zone` | Зона доступности хоста |
| `redis_password` | Пароль доступа (sensitive) |

## Outputs

| Output | Описание |
|---|---|
| `cluster_id` | ID кластера |
| `fqdn` | FQDN хоста кластера |
