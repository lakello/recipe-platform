# Окружение staging

Terraform-конфигурация для окружения `staging`. Используется для проверки релизов перед выкаткой в production.

## Назначение

Staging максимально приближен к production по настройкам безопасности, ресурсам и конфигурации. Деплой в staging выполняется из веток `release/*`.

## Структура

```
envs/staging/
  providers.tf              # Yandex Cloud provider
  backend.tf                # S3 remote backend (Yandex Object Storage)
  backend.hcl.example       # шаблон credentials для backend (не коммитится)
  variables.tf              # входные переменные (cloud_id, folder_id)
  outputs.tf                # пусто — требует заполнения
  terraform.tfvars.example  # пример значений переменных
  terraform.tfvars          # реальные значения (не коммитится)
  Makefile                  # команды init/plan/apply/destroy/fmt/validate
  authorized_key.json       # ключ сервисного аккаунта (не коммитится)
```

## Текущий статус

🚧 **Базовая структура создана, конфигурация модулей не реализована.**

Создано:
- Remote backend (S3 в Yandex Object Storage).
- Yandex Cloud provider.
- Makefile с командами.

Отсутствует:
- `main.tf` — подключение модулей (`network`, `kubernetes`, `postgres`, `redis`, `object-storage`, `compute`, `dns`).
- Полный `variables.tf` — переменные всех модулей.
- Полный `outputs.tf` — outputs окружения.
- `data.tf` — data sources (например, образ для bastion VM).

## Связи с проектом

Staging использует те же Terraform-модули из `modules/`, что и dev, но с production-like конфигурацией (большие ресурсы, `deletion_protection` для БД, persistence для Redis).

## Команды

```bash
make init     # terraform init -backend-config=backend.hcl
make plan     # fmt + validate + terraform plan
make apply    # terraform apply
make destroy  # terraform destroy
make fmt      # terraform fmt -recursive
make validate # terraform validate
```

## Важно для разработки

- Никогда не коммитить `terraform.tfvars`, `authorized_key.json`, `backend.hcl` — они в `.gitignore`.
- При создании `main.tf` опираться на `envs/dev/main.tf` как на образец, увеличив ресурсы до production-like.
- Staging должен максимально повторять production-конфигурацию, чтобы деплои на staging были репрезентативными.
