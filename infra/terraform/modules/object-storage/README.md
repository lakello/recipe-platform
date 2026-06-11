# Модуль object-storage

Terraform-модуль для создания Yandex Object Storage bucket с настройкой IAM-доступа.

## Что создаёт

- `yandex_storage_bucket` — bucket с versioning, lifecycle rules и CORS policy
- `yandex_iam_service_account` — сервисный аккаунт для доступа приложения к bucket
- `yandex_resourcemanager_folder_iam_member` — роль `storage.editor` для сервисного аккаунта
- `yandex_iam_service_account_static_access_key` — статический ключ (access_key + secret_key) для S3-совместимого доступа

## Переменные

| Переменная        | Тип                    | Описание                                              |
|-------------------|------------------------|-------------------------------------------------------|
| `bucket_config`   | `map(object({...}))`   | Конфигурация бакетов: ключ — имя, значение — настройки |
| `access_key`      | `string`               | Access key ID для S3 API (Terraform)                  |
| `secret_key`      | `string` (sensitive)   | Secret key для S3 API (Terraform)                     |
| `folder_id`       | `string`               | ID папки в Yandex Cloud для назначения IAM-прав        |
| `allowed_origins` | `list(string)`         | Разрешённые origins для CORS (default: localhost:3000) |

### Структура bucket_config

```hcl
bucket_config = {
  "bucket-name" = {
    versioning = bool
  }
}
```

## Outputs

| Output               | Описание                                    |
|----------------------|---------------------------------------------|
| `access_key_id`      | Access key ID сервисного аккаунта приложения |
| `secret_access_key`  | Secret key (sensitive)                      |

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

  access_key      = var.service_access_id
  secret_key      = var.service_access_key
  folder_id       = var.folder_id
  allowed_origins = ["https://app.example.com"]
}
```
