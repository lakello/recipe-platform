# Окружение prod

Terraform-конфигурация для окружения `production`. Публичное стабильное окружение.

## Назначение

Production — основное окружение, доступное конечным пользователям. Любые изменения в production применяются только после manual approval в CI/CD и после успешной проверки на staging.

## Структура

```
envs/prod/
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
- `data.tf` — data sources.

## Связи с проектом

Production использует те же Terraform-модули из `modules/`, что и dev/staging, но с максимальными ресурсами, `deletion_protection`, резервным копированием и строгими security settings.

## Команды

```bash
make init     # terraform init -backend-config=backend.hcl
make plan     # fmt + validate + terraform plan
make apply    # terraform apply (требует осторожности)
make destroy  # terraform destroy (ОПАСНО — только с явного согласия)
make fmt      # terraform fmt -recursive
make validate # terraform validate
```

## Важно для разработки

- Никогда не коммитить `terraform.tfvars`, `authorized_key.json`, `backend.hcl` — они в `.gitignore`.
- `terraform apply` в production выполняется только после успешного staging-деплоя и manual approval.
- `terraform destroy` в production недопустим без явного согласования.
- БД и Redis должны иметь `deletion_protection = true`.
- Terraform state хранится в отдельном production-бакете с versioning.
- Любые изменения инфраструктуры review-ятся перед применением через PR и `terraform plan`.
