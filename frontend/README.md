# Frontend

Frontend Recipe Platform — web-приложение платформы рецептов и планирования питания.

Приложение предоставляет пользовательский интерфейс для просмотра рецептов, регистрации и авторизации, создания рецептов, планирования питания, формирования списка покупок, работы с профилем, комментариями, подписками и модерацией.

## Назначение директории

В директории `frontend/` находится код web-клиента:

- React-приложение;
- TypeScript-код;
- страницы приложения;
- UI-компоненты;
- клиент для Backend API;
- управление состоянием;
- маршрутизация;
- стили;
- тесты;
- Dockerfile для сборки frontend image;
- Nginx-конфигурация для production-раздачи статики.

## Технологический стек

Планируемый стек frontend:

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS
- ESLint
- Prettier
- Vitest
- Testing Library
- Docker
- Nginx

## Ответственность frontend

Frontend отвечает за:

- публичный просмотр рецептов;
- поиск и фильтрацию рецептов;
- регистрацию и авторизацию;
- OAuth login через Google и Яндекс;
- хранение и обновление access token;
- работу с refresh token через backend;
- отображение профиля пользователя;
- редактирование профиля;
- загрузку аватара;
- создание и редактирование рецептов;
- загрузку фотографий рецептов;
- лайки;
- избранное;
- комментарии;
- подписки на авторов;
- недельный план питания;
- список покупок;
- уведомления;
- жалобы на контент;
- интерфейс модератора;
- интерфейс администратора;
- обработку ошибок API;
- отображение loading/error/success состояний.

## Предполагаемая структура

```text

frontend/

public/

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

admin/

moderation/

widgets/

features/

entities/

shared/

api/

config/

ui/

lib/

types/

tests/

Dockerfile

nginx.conf

package.json

vite.config.ts

tsconfig.json

README.md
```

Структура может быть организована по Feature-Sliced Design или близкому модульному подходу.

## Основные разделы приложения

### Публичная часть

Доступна гостям без авторизации:

- главная страница;
- список публичных рецептов;
- поиск рецептов;
- фильтрация по категориям;
- страница рецепта;
- публичный профиль автора;
- страницы регистрации и входа.

### Пользовательская часть

Доступна авторизованным пользователям:

- личный профиль;
- редактирование профиля;
- создание рецепта;
- редактирование своих рецептов;
- избранные рецепты;
- лайки;
- комментарии;
- подписки;
- недельный план питания;
- список покупок;
- уведомления;
- жалобы на контент.

### Модераторская часть

Доступна пользователям с ролью `moderator`:

- список жалоб;
- просмотр спорного контента;
- скрытие рецептов;
- скрытие или удаление комментариев;
- предупреждения пользователям;
- история модерации.

### Административная часть

Доступна пользователям с ролью `admin`:

- управление пользователями;
- назначение ролей;
- управление категориями;
- просмотр audit logs;
- техническая статистика;
- системные настройки.

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

 /moderation
 /moderation/reports
 /moderation/actions

 /admin
 /admin/users
 /admin/categories
 /admin/audit
 /admin/settings
```

## Работа с Backend API

Backend API доступен через переменную окружения:

```
VITE_API_BASE_URL=http://localhost:8000/api
```

Пример клиента:

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getRecipes() {
  const response = await fetch(`${API_BASE_URL}/recipes`);

  if (!response.ok) {
    throw new Error("Failed to load recipes");
  }

  return response.json();
}
```

Для серверного состояния используется TanStack Query:

- кэширование запросов;
- автоматический refetch;
- invalidation после мутаций;
- обработка loading/error states;
- retry logic.

## Аутентификация

Frontend работает с JWT-токенами, которые выдаёт backend.

Общий сценарий:

1. 1.Пользователь выполняет login.
2. 2.Backend возвращает access token и refresh token или устанавливает refresh token в cookie.
3. 3.Frontend использует access token для запросов к API.
4. 4.При истечении access token выполняется refresh.
5. 5.При logout токены удаляются, backend инвалидирует refresh session.

Рекомендуемый подход:

- access token хранить в памяти приложения или в безопасном state-слое;
- refresh token по возможности хранить в `HttpOnly Secure SameSite` cookie;
- не хранить чувствительные токены в localStorage для production;
- обрабатывать `401 Unauthorized` централизованно;
- использовать route guards для защищённых страниц.

## OAuth

Frontend должен поддерживать вход через:

- Google OAuth;
- Яндекс OAuth.

Сценарий:

1. 1.Пользователь нажимает кнопку входа через провайдера.
2. 2.Frontend перенаправляет пользователя на backend endpoint:

```
/api/auth/google/login
/api/auth/yandex/login
```

1. 1.Backend выполняет OAuth flow.
2. 2.После успешного входа пользователь возвращается на frontend callback page.
3. 3.Frontend обновляет состояние авторизации.

## Переменные окружения

Пример `.env.local`:

```env
VITE_APP_ENV=local
VITE_APP_NAME=Recipe Platform
VITE_API_BASE_URL=http://localhost:8000/api
VITE_PUBLIC_SITE_URL=http://localhost:5173
```

Важно: переменные `VITE_*` попадают в frontend bundle. Нельзя хранить в них секреты.

## Локальный запуск

Установить зависимости:

```bash
cd frontend

npm install
```

Запустить dev-сервер:

```
npm run dev
```

Приложение будет доступно по адресу:

```
http://localhost:5173
```

## Запуск через Docker Compose

Рекомендуемый запуск всего проекта выполняется из корня репозитория:

```
docker compose up -d
```

Frontend будет работать вместе с backend, PostgreSQL, Redis, OpenSearch, MinIO и другими local-зависимостями.

## Основные команды

Установка зависимостей:

```
npm install
```

Запуск dev-сервера:

```
npm run dev
```

Production build:

```
npm run build
```

Preview production build:

```
npm run preview
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

Tests with coverage:

```
npm run test:coverage
```

## Docker

Frontend собирается в отдельный Docker image.

Ожидаемый production-подход:

1. 1.На первом этапе Docker build собирает React-приложение через Vite.
2. 2.На втором этапе Nginx отдаёт собранную статику.
3. 3.Nginx добавляет security headers, gzip/brotli и cache headers.

Пример сборки:

```
docker build -t recipe-frontend:local .
```

Пример запуска:

```
docker run --rm -p 8080:80 recipe-frontend:local
```

Приложение будет доступно:

```
http://localhost:8080
```

## Nginx

В production frontend image используется Nginx.

Nginx отвечает за:

- отдачу статических файлов;
- fallback на `index.html` для SPA routes;
- gzip/brotli сжатие;
- cache-control для assets;
- security headers;
- health endpoint для Kubernetes.

Пример SPA fallback:

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

## Работа с изображениями

Фотографии рецептов и аватары пользователей хранятся в Object Storage.

Frontend не загружает файлы через backend напрямую.

Рекомендуемый сценарий:

1. 1.Пользователь выбирает файл.
2. 2.Frontend проверяет базовые ограничения:
   - размер;
   - тип файла;
   - расширение.

3. 3.Frontend запрашивает у backend pre-signed upload URL.
4. 4.Frontend загружает файл напрямую в Object Storage.
5. 5.Frontend сообщает backend metadata загруженного файла.
6. 6.Backend сохраняет запись в БД.
7. 7.Worker создаёт thumbnail.

Поддерживаемые форматы:

- JPEG;
- PNG;
- WebP.

## UI-состояния

Для production-like качества интерфейс должен обрабатывать:

- loading state;
- empty state;
- error state;
- unauthorized state;
- forbidden state;
- validation errors;
- optimistic updates;
- offline или network error;
- retry action;
- skeleton loading.

## Формы

Для форм необходимо предусмотреть:

- клиентскую валидацию;
- отображение ошибок backend;
- disabled state во время отправки;
- защиту от повторной отправки;
- обработку успешного результата;
- доступность с клавиатуры.

Основные формы:

- регистрация;
- вход;
- редактирование профиля;
- создание рецепта;
- редактирование рецепта;
- комментарий;
- жалоба;
- план питания;
- элемент списка покупок;
- управление категорией.

## Роли и доступы

Frontend должен скрывать или блокировать интерфейс в зависимости от роли пользователя.

При этом защита на frontend не является security boundary.

Все права обязательно проверяются на backend.

Примеры:

| Роль          | Доступ                         |
| ------------- | ------------------------------ |
| Гость         | Публичные страницы             |
| Пользователь  | Профиль, рецепты, план питания |
| Модератор     | Модераторская панель           |
| Администратор | Админ-панель                   |

## Тестирование

Для frontend-тестов используются:

- Vitest;
- Testing Library;
- возможно Playwright для e2e.

Покрывать тестами нужно:

- утилиты;
- API-клиент;
- auth flow;
- route guards;
- формы;
- ключевые компоненты;
- meal plan;
- shopping list;
- moderator/admin screens.

Запуск unit/component tests:

```
npm run test
```

Запуск e2e, если будет добавлен Playwright:

```
npm run test:e2e
```

## Accessibility

Frontend должен учитывать базовые требования доступности:

- корректная семантика HTML;
- label для form controls;
- доступность с клавиатуры;
- focus states;
- alt для изображений;
- aria-атрибуты там, где они действительно нужны;
- достаточный контраст;
- понятные сообщения об ошибках.

## Performance

Требования к производительности:

- главная страница открывается до 2 секунд;
- использовать code splitting;
- lazy loading страниц;
- оптимизация изображений;
- cache-control для static assets;
- минимизация bundle size;
- избегать лишних rerender;
- использовать TanStack Query cache;
- отображать skeleton loading.

## Observability

Frontend должен быть готов к observability:

- логирование ошибок клиента;
- correlation/request ID для API-запросов;
- поддержка trace context, если будет подключена;
- сбор frontend metrics в перспективе;
- интеграция с внешним error tracking может быть добавлена позже.

## Security

Основные требования:

- не хранить секреты в frontend;
- не помещать чувствительные данные в `VITE_*`;
- аккуратно работать с JWT;
- использовать HTTPS в dev/staging/prod;
- обрабатывать XSS-риски;
- не рендерить HTML от пользователей без санитайза;
- валидировать файлы перед загрузкой;
- ограничивать CORS на backend;
- использовать security headers на Nginx;
- не полагаться на frontend-проверки прав.

## Kubernetes

В Kubernetes frontend запускается как отдельный Deployment.

Требования:

- минимум 2 реплики в production;
- readinessProbe;
- livenessProbe;
- resource requests;
- resource limits;
- Nginx-based image;
- non-root там, где возможно;
- PodDisruptionBudget;
- HorizontalPodAutoscaler;
- NetworkPolicy;
- Ingress route через Nginx Ingress Controller.

## CI/CD

Frontend участвует в GitHub Actions pipelines.

На Pull Request выполняются:

- install dependencies;
- lint;
- type check;
- tests;
- production build;
- Docker build;
- security scan.

На deploy pipeline:

- сборка Docker image;
- push image в GHCR;
- deploy через Helm;
- smoke tests.

## Smoke tests

Минимальные smoke tests после деплоя:

```http
## GET /
GET /health
```

Дополнительно:

- открывается главная страница;
- frontend доступен по HTTPS;
- SPA fallback работает;
- frontend может обратиться к backend API;
- страница login открывается;
- страница рецептов открывается.

## Интеграция с окружениями

Пример доменов:

| Окружение  | Frontend                      |
| ---------- | ----------------------------- |
| local      | `http://localhost:5173`       |
| dev        | `https://dev.example.com`     |
| staging    | `https://staging.example.com` |
| production | `https://example.com`         |

Backend API:

| Окружение  | API                                   |
| ---------- | ------------------------------------- |
| local      | `http://localhost:8000/api`           |
| dev        | `https://api.dev.example.com/api`     |
| staging    | `https://api.staging.example.com/api` |
| production | `https://api.example.com/api`         |

## Что уже реализовано

### Авторизация (feat/frontend-auth)

- **Зависимости:** react-hook-form, zod, @hookform/resolvers
- `src/shared/api/client.ts` — `credentials: 'include'`, автоматический refresh при 401
- `src/features/auth/` — API и хуки: `useLogin`, `useRegister`, `useLogout`
- `src/features/profile/` — API и хуки: `useCurrentUser`, `useUpdateProfile`
- `src/app/router/ProtectedRoute.tsx` — защищённые маршруты (редирект на `/login`)
- `src/shared/ui/` — компоненты `Input`, `Button`

Страницы:

| Путь | Описание | Auth |
|---|---|---|
| `/login` | Форма входа | Публичная |
| `/register` | Форма регистрации | Публичная |
| `/profile` | Просмотр и редактирование username | 🔒 |

### Инициализация React (feat/frontend-init)

- Vite 8 + React 19 + TypeScript
- React Router v7, TanStack Query v5, Tailwind CSS v3
- Path alias `@/` → `src/`
- FSD-структура: `app/`, `pages/`, `widgets/`, `features/`, `entities/`, `shared/`
- `src/app/App.tsx` — BrowserRouter + QueryProvider + маршруты
- `src/pages/main-page/` — главная страница (`/`)
- `src/shared/api/client.ts` — базовый fetch-клиент
- `src/shared/config/env.ts` — `VITE_API_BASE_URL` из env
- `.env.example` с примером переменных окружения

Команды:

```bash
npm run dev        # dev-сервер → http://localhost:5173
npm run build      # production-сборка
npm run typecheck  # проверка типов
npm run lint       # ESLint
```

## Статус

Frontend находится в разработке.

Приоритет реализации:

1. ~~Базовая структура Vite + React + TypeScript.~~ ✓
2. ~~Routing.~~ ✓
3. ~~API client.~~ ✓
4. ~~Auth pages.~~ ✓
5. Layout.
6. Recipes list.
7. Recipe details.
8. Recipe create/edit.
9. Profile.
10. Comments, likes, favorites.
11. Meal plan.
12. Shopping list.
13. Moderation UI.
14. Admin UI.
15. UI polish, accessibility, performance.
