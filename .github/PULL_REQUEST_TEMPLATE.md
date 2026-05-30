# Pull Request

## Описание

Кратко опиши, что изменено в этом Pull Request.

<!--

Пример:

- Добавлен endpoint авторизации по email

- Обновлён Helm chart для backend

- Добавлен Terraform module для Redis

-->

## Тип изменений

Отметь подходящие варианты:

- [ ] `feat` — новая функциональность
- [ ] `fix` — исправление ошибки
- [ ] `docs` — документация
- [ ] `refactor` — рефакторинг
- [ ] `test` — тесты
- [ ] `ci` — изменения CI/CD
- [ ] `infra` — инфраструктура, Terraform, Ansible, Kubernetes, Helm
- [ ] `chore` — служебные изменения
- [ ] `security` — изменения, связанные с безопасностью

## Связанная задача

<!-- Если есть issue/task, укажи ссылку -->

Closes #

## Затронутые компоненты

Отметь компоненты, которых касается PR:

- [ ] Backend
- [ ] Frontend Web
- [ ] Android
- [ ] Desktop
- [ ] PostgreSQL / миграции
- [ ] Redis / Celery
- [ ] OpenSearch
- [ ] Docker
- [ ] Docker Compose
- [ ] Kubernetes manifests
- [ ] Helm chart
- [ ] Terraform
- [ ] Ansible
- [ ] GitHub Actions
- [ ] Monitoring / Logging / Tracing
- [ ] Documentation
## Окружения

Отметь окружения, на которые влияет изменение:

- [ ] Local
- [ ] Dev
- [ ] Staging
- [ ] Production

## Что было сделано

<!-- Список основных изменений -->
-
-
-

## Как проверить

Опиши шаги для проверки.

``` bash
# пример

docker compose up --build
```

Проверить:

-  приложение запускается локально
-  backend healthcheck отвечает
-  frontend открывается
-  тестируемый сценарий работает

## Тесты

Отметь выполненные проверки:

-  Backend lint пройден
-  Backend unit tests пройдены
-  Frontend lint пройден
-  Frontend unit tests пройдены
-  Type checks пройдены
-  Docker build успешен
-  Docker Compose запускался локально
-  Helm template/lint успешен
-  Terraform fmt/validate успешен
-  Ansible lint/syntax-check успешен
-  Smoke tests пройдены
-  E2E tests пройдены
-  Не требуется

## Миграции базы данных

Есть ли миграции БД?

-  Нет
-  Да, добавлены Alembic migrations

Если да, опиши:

- какие таблицы/поля изменены;
- обратима ли миграция;
- требуется ли downtime;
- проверялась ли миграция локально/staging.

## Инфраструктурные изменения

Есть ли изменения инфраструктуры?

-  Нет
-  Да, Terraform
-  Да, Ansible
-  Да, Kubernetes
-  Да, Helm
-  Да, GitHub Actions
-  Да, Monitoring/Logging/Tracing

Если да, опиши влияние:

- какие ресурсы создаются/изменяются/удаляются;
- влияет ли это на dev/staging/prod;
- нужен ли manual action;
- есть ли риск downtime.

## Безопасность

Проверь:

-  Секреты не добавлены в Git
-  `.env` файлы с реальными значениями не закоммичены
-  Логи не содержат пароли, токены или персональные данные
-  Docker image не содержит секреты
-  Kubernetes Secret не содержит реальные значения в plain YAML
-  Используются минимально необходимые права доступа
-  Валидация входных данных добавлена/не требуется
-  Rate limiting/CORS/Auth проверены, если изменение связано с API

## Observability

Если изменение влияет на runtime-поведение, проверь:

-  Добавлены/обновлены структурированные логи
-  Метрики добавлены/обновлены
-  Tracing не сломан
-  Alerting не требует изменений
-  Dashboard не требует изменений
-  Не применимо

## Скриншоты

Если PR меняет UI, добавь скриншоты или видео.

|До|После|
|---|---|
|||

## Чеклист перед merge

-  Ветка актуальна относительно целевой ветки
-  Нет конфликтов
-  CI прошёл успешно
-  Code review пройден
-  Документация обновлена, если нужно
-  Breaking changes описаны
-  Rollback plan описан для risky changes
-  PR готов к merge

## Breaking changes

Есть ли несовместимые изменения?

-  Нет
-  Да

Если да, опиши:

- что ломается;
- кого это затрагивает;
- как мигрировать.

## Rollback plan

Опиши, как откатить изменение, если после deploy возникнут проблемы.

<!-- Пример: - Откатить Helm release на предыдущую revision - Вернуть предыдущий Docker image tag - Откатить PR revert-коммитом - Для миграций БД использовать downgrade, если безопасно -->