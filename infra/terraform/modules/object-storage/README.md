# Модуль object-storage

Terraform-модуль для создания Yandex Object Storage bucket с настройкой IAM-доступа.

## Что создаёт

- `yandex_storage_bucket` — bucket с versioning, lifecycle rules и CORS policy
- `yandex_storage_bucket_iam_binding` — bucket-scoped доступ runtime service account

Сервисный аккаунт создаётся в `modules/iam`; модуль получает его ID и назначает `storage.editor` только созданному bucket.

## Переменные

| Переменная        | Тип                    | Описание                                              |
|-------------------|------------------------|-------------------------------------------------------|
| `bucket_config`   | `map(object({...}))`   | Конфигурация бакетов: ключ — имя, значение — настройки |
| `storage_sa_id`   | `string`               | ID runtime service account из модуля iam              |
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

  storage_sa_id   = module.iam.storage_sa_id
  allowed_origins = ["https://app.example.com"]
}
```
