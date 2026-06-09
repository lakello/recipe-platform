# Desktop

Desktop-приложение Recipe Platform — клиент платформы рецептов и планирования питания для Windows и Linux.

Приложение позволяет пользователям работать с рецептами, планом питания и списком покупок с настольного компьютера. Desktop-клиент использует тот же Backend API, что web и Android-приложения.

## Назначение директории

В директории `desktop/` находится код desktop-приложения:

- Tauri-приложение;
- React frontend для desktop-клиента;
- Rust runtime;
- конфигурация сборки Windows и Linux;
- интеграция с Backend API;
- управление локальным состоянием;
- desktop-специфичные функции;
- тесты;
- CI-конфигурация сборки desktop-артефактов.

## Технологический стек

Планируемый стек desktop:

- Tauri
- React
- TypeScript
- Vite
- Rust
- TanStack Query
- React Router
- Tailwind CSS
- Tauri APIs
- ESLint
- Prettier
- Vitest

Целевые платформы:

- Windows
- Linux

## Почему Tauri

Tauri выбран для desktop-клиента, потому что:

- легче Electron;
- использует системный WebView;
- позволяет переиспользовать React-подходы;
- имеет Rust runtime;
- даёт меньший размер приложения;
- подходит для сборки под Windows и Linux;
- хорошо подходит для pet-проекта advanced-уровня.

## Ответственность desktop-приложения

Desktop-клиент отвечает за:

- просмотр публичных рецептов;
- поиск и фильтрацию рецептов;
- просмотр страницы рецепта;
- регистрацию и вход;
- OAuth login через браузер;
- профиль пользователя;
- избранные рецепты;
- лайки;
- комментарии;
- подписки;
- недельный план питания;
- список покупок;
- локальное кэширование части данных;
- desktop-уведомления, если будут добавлены;
- обработку ошибок API;
- безопасную работу с пользовательской сессией.

## Предполагаемая структура

```text

desktop/

src/

app/

providers/

router/

styles/

pages/

home/

auth/

recipes/

profile/

meal-plan/

shopping-list/

settings/

features/

entities/

shared/

api/

config/

ui/

lib/

types/

src-tauri/

src/

main.rs

icons/

capabilities/

tauri.conf.json

Cargo.toml

public/

tests/

package.json

vite.config.ts

tsconfig.json

README.md
```

## Связь с web frontend

Desktop-приложение может частично переиспользовать подходы из `frontend/`:

- UI-компоненты;
- API-клиент;
- типы;
- формы;
- валидацию;
- бизнес-логику отображения.

При этом desktop-клиент имеет собственную директорию, потому что:

- у него отдельная сборка;
- есть Rust runtime;
- есть Tauri permissions/capabilities;
- есть платформенные артефакты;
- могут быть desktop-специфичные функции;
- отличается работа с OAuth/deep links;
- отличается packaging.

## Основные экраны

### Публичные экраны

- Главная;
- Список рецептов;
- Поиск;
- Фильтры;
- Детальная страница рецепта;
- Публичный профиль автора;
- Login;
- Register.

### Пользовательские экраны

- Личный профиль;
- Редактирование профиля;
- Избранное;
- Мои рецепты;
- Создание рецепта;
- Редактирование рецепта;
- План питания;
- Список покупок;
- Уведомления;
- Настройки.

### Дополнительные desktop-возможности

Позже можно добавить:

- desktop notifications;
- экспорт списка покупок в файл;
- локальный cache;
- быстрые горячие клавиши;
- системный tray;
- auto-update.

## Маршруты приложения

Примерная структура маршрутов:

```
/
 /login
 /register
 /oauth/callback

 /recipes
 /recipes/:recipeId
 /recipes/new
 /recipes/:recipeId/edit

 /users/:username
 /profile
 /profile/edit
 /favorites

 /meal-plan
 /shopping-list
 /notifications
 /settings
```

## Работа с Backend API

Desktop-клиент использует общий Backend API.

Базовый URL зависит от окружения:

```
local:      http://localhost:8000/api
dev:        https://api.dev.example.com/api
staging:    https://api.staging.example.com/api
production: https://api.example.com/api
```

Пример переменных окружения для Vite:

```
VITE_APP_ENV=local
VITE_API_BASE_URL=http://localhost:8000/api
VITE_PUBLIC_SITE_URL=http://localhost:1420
```

Переменные `VITE_*` попадают в bundle. Нельзя хранить в них секреты.

## Аутентификация

Desktop-клиент использует JWT access token и refresh token, которые выдаёт backend.

Общий сценарий:

1. 1.Пользователь выполняет login.
2. 2.Backend возвращает access token и refresh token или session data.
3. 3.Desktop-клиент использует access token для запросов.
4. 4.При истечении access token выполняется refresh.
5. 5.При logout клиент очищает локальную сессию.

Пример заголовка:

```
Authorization: Bearer <access-token>
```

## Безопасное хранение сессии

Для desktop важно не хранить чувствительные данные в открытом виде.

Возможные подходы:

- использовать Tauri plugin для secure storage;
- использовать системные keychain/keyring механизмы;
- хранить access token только в памяти;
- refresh token хранить только в защищённом хранилище;
- очищать токены при logout.

Не рекомендуется хранить refresh token в plain text файлах.

## OAuth

OAuth через Google и Яндекс выполняется через внешний браузер.

Ожидаемый сценарий:

1. 1.Пользователь нажимает кнопку входа через Google или Яндекс.
2. 2.Приложение открывает backend endpoint:

```
/api/auth/google/login
/api/auth/yandex/login
```

1. Backend выполняет OAuth flow.
2. 2.После успешного входа backend возвращает пользователя в desktop-приложение через deep link или локальный callback.
3. 3.Desktop-клиент завершает авторизацию и обновляет состояние сессии.

Пример deep link:

```
recipeplatform://oauth/callback
```

Реализация OAuth для desktop должна быть отдельно проверена для Windows и Linux.

## Работа с изображениями

Фотографии рецептов и аватары пользователей хранятся в Object Storage.

Сценарий загрузки:

1. 1.Пользователь выбирает файл через desktop file dialog.
2. 2.Desktop-клиент проверяет размер и тип файла.
3. 3.Клиент запрашивает pre-signed URL у backend.
4. 4.Файл загружается напрямую в Object Storage.
5. 5.Клиент отправляет metadata файла в backend.
6. 6.Backend сохраняет запись в БД.
7. 7.Worker генерирует thumbnail.

Поддерживаемые форматы:

- JPEG;
- PNG;
- WebP.

## Локальные возможности

Desktop-клиент может использовать Tauri APIs для:

- выбора файлов;
- сохранения экспортированных списков покупок;
- desktop notifications;
- открытия ссылок в браузере;
- системных диалогов;
- локального storage;
- работы с auto-update.

Любой доступ к системным API должен быть явно разрешён через Tauri capabilities.

## Tauri permissions

Tauri требует явно описывать разрешения.

Нужно придерживаться принципа минимальных прав:

- разрешать только нужные API;
- не включать лишние capabilities;
- не давать доступ к файловой системе шире необходимого;
- проверять команды Rust-side;
- валидировать входные параметры команд.

## Локальный запуск

Установить зависимости:

``` bash
cd desktop

npm install
```

Запустить desktop-приложение в dev-режиме:

```
npm run tauri dev
```

Обычно приложение будет использовать Vite dev server и Tauri shell.

## Сборка

Production build:

```
npm run tauri build
```

Результаты сборки будут находиться в директориях Tauri build output внутри `src-tauri/target/`.

Примерные артефакты:

### Windows

- `.msi`
- `.exe`

### Linux

- `.deb`
- `.AppImage`
- `.rpm`, если будет настроено

## Основные команды

Установка зависимостей:

```
npm install
```

Запуск Vite dev server:

```
npm run dev
```

Запуск Tauri dev:

```
npm run tauri dev
```

Сборка frontend:

```
npm run build
```

Сборка desktop app:

```
npm run tauri build
```

Lint:

```
npm run lint
```

Format:

```
npm run format
```

Type check:

```
npm run typecheck
```

Tests:

```
npm run test
```

Rust checks:

``` bash
cd src-tauri

cargo check

cargo test

cargo clippy

cargo fmt --check
```

## Тестирование

Для TypeScript/React части:

- Vitest;
- Testing Library;
- ESLint;
- TypeScript checks.

Для Rust/Tauri части:

- cargo test;
- cargo clippy;
- cargo fmt.

Что нужно покрывать тестами:

- API-клиент;
- auth flow;
- route guards;
- формы;
- утилиты;
- Tauri commands;
- работу с настройками;
- обработку ошибок.

## Конфигурация окружений

Рекомендуется поддерживать несколько окружений:

```
local
dev
staging
production
```

Пример:

``` env
VITE_APP_ENV=dev
VITE_API_BASE_URL=https://api.dev.example.com/api
```

Для production-сборки:

``` env
VITE_APP_ENV=production
VITE_API_BASE_URL=https://api.example.com/api
```

Секреты нельзя хранить в `.env` файлах, попадающих в Git.

## Security

Основные требования безопасности:

- не хранить секреты в frontend bundle;
- не хранить refresh token в plain text;
- использовать HTTPS для dev/staging/prod;
- проверять OAuth callback/deep links;
- минимизировать Tauri permissions;
- валидировать аргументы Tauri commands;
- не логировать токены;
- не логировать персональные данные;
- не рендерить пользовательский HTML без санитайза;
- обновлять зависимости;
- проверять Rust dependencies;
- подписывать production-сборки, если будет настроено.

## Updates

Tauri поддерживает механизм auto-update.

Для pet-проекта можно добавить позже:

- публикацию release artifacts в GitHub Releases;
- manifest обновлений;
- подпись обновлений;
- проверку версии при старте приложения.

На первом этапе auto-update не обязателен.

## Observability

Desktop-клиент может поддерживать:

- локальные debug-логи;
- сбор crash reports в перспективе;
- correlation ID для API-запросов;
- user-friendly сообщения об ошибках;
- экспорт диагностической информации для отладки.

В production нельзя сохранять чувствительные данные в логах.

## UX-требования

Приложение должно обрабатывать:

- loading state;
- empty state;
- error state;
- offline state;
- unauthorized state;
- forbidden state;
- retry action;
- long-running operations;
- ошибки сети;
- недоступность backend.

## Accessibility

Нужно учитывать:

- keyboard navigation;
- focus states;
- корректную семантику HTML;
- достаточный контраст;
- readable font sizes;
- alt для изображений;
- понятные сообщения об ошибках.

## CI/CD

Desktop-приложение может собираться через GitHub Actions.

На Pull Request:

- install dependencies;
- lint;
- type check;
- tests;
- cargo check;
- cargo clippy;
- frontend build.

На release pipeline:

- сборка Windows artifact;
- сборка Linux artifact;
- публикация артефактов в GitHub Releases;
- опциональная подпись;
- опциональная настройка auto-update.

Сборка под разные ОС обычно выполняется на разных GitHub Actions runners:

- `windows-latest`;
- `ubuntu-latest`.

## Связь с инфраструктурой

Desktop-приложение не разворачивается в Kubernetes.

Но оно зависит от backend API, который работает в Yandex Managed Kubernetes и доступен через HTTPS-домен.

Production desktop-клиент должен обращаться к:

```
https://api.example.com/api
```

## Статус

Не начато. Запланировано на следующий этап.

После второго этапа разработки директория `desktop/` содержит только этот README.

Разработка desktop-приложения начнётся после завершения инфраструктурного этапа (DevOps).

Приоритет реализации:

1. Базовый Tauri-проект.
2. React + TypeScript + Vite.
3. API client.
4. Auth flow.
5. Recipes list.
6. Recipe details.
7. Search.
8. Favorites.
9. Meal plan.
10. Shopping list.
11. Profile.
12. File upload.
13. Desktop packaging.
14. Windows/Linux build в CI.
