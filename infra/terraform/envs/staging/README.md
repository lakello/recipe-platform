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
  data.tf                   # data sources (образ bastion VM)
  main.tf                   # подключение Terraform-модулей
  variables.tf              # входные переменные окружения
  outputs.tf                # outputs окружения
  terraform.tfvars.example  # пример значений переменных
  terraform.tfvars          # реальные значения (не коммитится)
  Makefile                  # команды init/plan/apply/destroy/fmt/validate
  authorized_key.json       # ключ сервисного аккаунта (не коммитится)
```

## Текущий статус

🚧 **Конфигурация подготовлена и проходит `terraform validate`; развёртывание окружения отложено.**

Подключены модули `network`, `iam`, `kubernetes`, `postgres`, `redis`, `object-storage`, `compute` и `dns`. Реальные cloud-ресурсы не создавались.

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

- Никогда не коммитить `terraform.tfvars`, `authorized_key.json`, `backend.hcl` — они в `.gitignore`; `backend.hcl` содержит секреты доступа к backend.
- Для staging должен использоваться отдельный ключ `staging/terraform.tfstate` в state bucket.
- State и plan-файлы считаются секретами: их нельзя публиковать в Git, задачах или CI-логах.
- Staging должен максимально повторять production-конфигурацию, чтобы деплои на staging были репрезентативными.
