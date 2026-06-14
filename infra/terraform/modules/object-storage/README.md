# Модуль object-storage

Terraform-модуль для создания Yandex Object Storage bucket с настройкой IAM-доступа.

## Что создаёт

- `yandex_storage_bucket` — bucket с versioning, lifecycle rules и CORS policy

Сервисный аккаунт, IAM-роль и статический ключ доступа создаются в модуле `modules/iam` и передаются сюда через переменные `access_key` и `secret_key`.

## Переменные

| Переменная        | Тип                    | Описание                                              |
|-------------------|------------------------|-------------------------------------------------------|
| `bucket_config`   | `map(object({...}))`   | Конфигурация бакетов: ключ — имя, значение — настройки |
| `access_key`      | `string`               | Access key ID для S3 API (из модуля iam)              |
| `secret_key`      | `string` (sensitive)   | Secret key для S3 API (из модуля iam)                 |
| `allowed_origins` | `list(string)`         | Разрешённые origins для CORS (default: localhost:3000) |

### Структура bucket_config

```hcl
bucket_config = {
  "bucket-name" = {
    versioning = bool
  }
}
```

## Lifecycle rules

Модуль настраивает два правила:

- `abort-incomplete-multipart-uploads` — удаляет незавершённые multipart uploads через 7 дней
- `cleanup-old-versions` — удаляет неактуальные версии объектов через 30 дней

## Пример использования

```hcl
module "object_storage" {
  source = "../../modules/object-storage"

  bucket_config = {
    "recipe-platform-bucket-dev" = {
      versioning = false
    }
  }

  access_key      = module.iam.access_key_id
  secret_key      = module.iam.secret_access_key
  allowed_origins = ["https://app.example.com"]
}
```
