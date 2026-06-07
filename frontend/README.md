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

### Лайки и избранное (feat/likes-and-favorites)

- `src/features/likes/api/likesApi.ts` — методы: like, unlike, addFavorite, removeFavorite, listFavorites
- `src/features/likes/hooks/useLikes.ts` — хуки: `useLike`, `useFavorite`, `useFavorites`; инвалидация кэша рецептов и избранного после каждой мутации
- `src/features/likes/ui/LikeButton.tsx` — кнопка лайка (❤️/🤍) с счётчиком; заблокирована для неавторизованных
- `src/features/likes/ui/FavoriteButton.tsx` — кнопка избранного (★/☆); заблокирована для неавторизованных
- `src/pages/favorites-page/` — страница `/favorites` с карточками избранных рецептов и кнопками лайка/избранного
- `Recipe` тип дополнен `likes_count`, `is_liked`, `is_favorited`

Страницы:

| Путь | Описание | Auth |
|---|---|---|
| `/favorites` | Список избранных рецептов | 🔒 |

Поведение:
- Кнопки лайка и избранного отображаются на карточках рецептов (`/recipes`) и на странице рецепта (`/recipes/:id`)
- Неавторизованный пользователь видит счётчик лайков, кнопки визуально заблокированы
- Кнопка «Избранное» в шапке страницы рецептов видна только авторизованным

### Комментарии (feat/comments)

- `src/features/comments/api/commentsApi.ts` — типы (`Comment`, `CommentPage`) и API-методы: list, listReplies, create, update, delete, hide, unhide
- `src/features/comments/hooks/useComments.ts` — хуки: `useComments`, `useReplies`, `useAddComment`, `useEditComment`, `useDeleteComment`, `useHideComment`, `useUnhideComment`; инвалидация кэша после мутаций
- `src/features/comments/ui/CommentForm.tsx` — переиспользуемая форма для добавления/редактирования/ответа
- `src/features/comments/ui/CommentItem.tsx` — один комментарий: инлайн-редактирование, удаление, кнопка «Ответить», раскрываемые ответы, кнопки скрытия/показа для модераторов
- `src/features/comments/ui/CommentList.tsx` — список комментариев с формой добавления; для неавторизованных — сообщение о необходимости войти
- `RecipePage` — добавлен блок комментариев внизу страницы рецепта

Поведение:
- Авторизованный пользователь может оставить комментарий и ответить на любой топ-уровневый комментарий
- Автор комментария видит кнопки «Изменить» и «Удалить» (soft delete)
- Модератор (admin/superadmin) видит кнопки «Скрыть» / «Показать»; тело скрытого комментария заменяется на плейсхолдер
- Удалённые комментарии сохраняют структуру треда (тело заменяется на «Комментарий удалён»)
- Ответы загружаются по клику «Показать ответы (N)»

**Fix (feat/comments):** кнопка «Редактировать» на странице рецепта использует `replace`-навигацию, чтобы edit-страница не накапливалась в истории браузера и не мешала кнопке «Назад».

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

### Категории (feat/categories)

- `src/features/categories/api/categoriesApi.ts` — типы и API-методы: list, get, create, update, delete
- `src/features/categories/hooks/useCategories.ts` — хуки: `useCategoriesList`, `useCreateCategory`, `useUpdateCategory`, `useDeleteCategory`
- `src/features/profile/api/profileApi.ts` — добавлен `role: UserRole` в `UserProfile`
- `RecipeForm` — выпадающий список выбора категории
- `RecipesListPage` — фильтр-теги по категориям, название категории на карточке рецепта

Страницы:

| Путь | Описание | Auth |
|---|---|---|
| `/admin/categories` | Управление категориями | 🔒 admin/superadmin |

Поведение:
- Кнопка "Категории" в шапке страницы рецептов видна только пользователям с ролью `admin` или `superadmin`
- Фильтр по категории — через кнопки-теги над списком рецептов; фильтрация выполняется на бэкенде

### Docker (feat/docker-compose-local)

- `Dockerfile` — multi-stage: Node 22 сборка → Nginx 1.25 раздача статики
- `nginx.conf` — SPA fallback (`try_files`), cache headers для статических ассетов
- `.dockerignore` — исключены `node_modules`, `dist`, `.env`, `.git`

### Загрузка фото (feat/uploads)

- `src/features/uploads/api/uploadsApi.ts` — методы: `presign`, `uploadToS3`, `attachRecipePhoto`, `deleteRecipePhoto`, `setAvatar`, `getViewUrl`
- `src/features/uploads/hooks/useUpload.ts` — хук `useRecipePhotoUpload` (presign → PUT в MinIO → attach)
- `src/features/uploads/ui/PhotoUpload.tsx` — компонент выбора и предпросмотра фото с кнопками «Добавить» / «Удалить»
- `RecipePage` — интегрирован `PhotoUpload` с отображением текущего фото рецепта

Сценарий загрузки (3 шага):
1. `POST /api/uploads/presign` — получить presigned PUT URL
2. `PUT <presigned_url>` — загрузить файл напрямую в MinIO (без прокси через бэкенд)
3. `POST /api/uploads/recipes/{id}/photo` — сообщить бэкенду ключ загруженного файла

### Ингредиенты и шаги (feat/ingredients-steps)

- `src/features/ingredients/api/ingredientsApi.ts` — типы и API-методы, `UNIT_LABELS` для отображения единиц
- `src/features/ingredients/hooks/useIngredients.ts` — хуки: `useIngredientSearch`, `useSetRecipeIngredients`, `useSetRecipeSteps`
- `src/features/ingredients/ui/IngredientsForm.tsx` — динамическая форма с автодополнением из глобального справочника
- `src/features/ingredients/ui/StepsForm.tsx` — DnD-сортируемая форма шагов (`@dnd-kit/core` + `@dnd-kit/sortable`); заголовок — обязательное поле, описание — опционально; при попытке сохранить шаг без заголовка показывается inline-ошибка
- `src/pages/recipe-page/ui/RecipePage.tsx` — отображение ингредиентов и шагов; автор редактирует прямо на странице

### Базовые рецепты (feat/frontend-recipes)

- `src/features/recipes/api/recipesApi.ts` — типы и API-методы: list, get, create, update, delete
- `src/features/recipes/hooks/useRecipes.ts` — хуки: `useRecipesList`, `useRecipe`, `useCreateRecipe`, `useUpdateRecipe`, `useDeleteRecipe`
- `src/features/recipes/ui/RecipeForm.tsx` — переиспользуемая форма (создание и редактирование)

Страницы:

| Путь | Описание | Auth |
|---|---|---|
| `/recipes` | Список опубликованных рецептов (grid) | Публичная |
| `/recipes/:recipeId` | Детали рецепта | Публичная |
| `/recipes/new` | Создание рецепта | 🔒 |
| `/recipes/:recipeId/edit` | Редактирование рецепта | 🔒 |
| `/recipes/drafts` | Мои черновики | 🔒 |
| `/users/:userId` | Публичный профиль пользователя | Публичная |

Поведение:
- Рецепт создаётся со статусом `draft`; автор публикует его кнопкой "Опубликовать" на странице рецепта
- Список рецептов показывает только опубликованные; черновики — на отдельной странице
- Кнопки редактирования, удаления и публикации видны только автору
- Профиль показывает все рецепты пользователя (включая черновики и приватные)
- После регистрации и входа — автоматический редирект на главную

### Карточки рецептов, отображение автора и публичные профили (feat/public-user-profiles)

**Бэкенд:**
- `GET /api/users/{user_id}` — публичный профиль пользователя (id, username, avatar_url, created_at); без email и приватных полей
- `GET /api/recipes?author_id=<uuid>` — фильтр рецептов по автору
- Схема `UserPublicRead` в `schemas/user.py`

**Фронтенд:**
- `src/shared/ui/UserLink.tsx` — переиспользуемый компонент: аватар (с инициалом-заглушкой) + никнейм → ссылка на `/users/:userId`; вызывает `e.stopPropagation()` для корректной работы внутри кликабельных карточек
- `src/features/recipes/ui/RecipeCard.tsx` — карточка рецепта: фото 16:9 (или gradient-заглушка), чипы категории/сложности/порций/времени, заголовок, кликабельный автор, кнопка лайка и счётчик комментариев; вся карточка кликабельна
- `src/features/profile/api/profileApi.ts` — `getPublicUser(userId)`, тип `UserPublicRead`; `getMe` переведён на нативный `fetch` без редиректа на 401 (чтобы неавторизованные гости могли просматривать публичные страницы)
- `src/features/profile/hooks/usePublicProfile.ts` — хук для загрузки публичного профиля
- `src/features/recipes/api/recipesApi.ts` — метод `listByAuthor(authorId)`
- `src/features/recipes/hooks/useRecipes.ts` — хук `useUserRecipes(authorId)`
- `src/pages/user-profile-page/` — страница публичного профиля: большой аватар, никнейм, дата регистрации, список опубликованных рецептов; режим только чтение

**Изменения существующих компонентов:**
- `RecipesListPage` — сетка 1/2/3 колонки, доступна без авторизации, auth-aware шапка
- `RecipePage` — блок автора (UserLink) под заголовком рецепта
- `CommentItem` — аватар и никнейм автора комментария кликабельны (UserLink)
- `App.tsx` — маршрут `/users/:userId` (публичный, без ProtectedRoute); `/` редиректит на `/recipes`

Страницы:

| Путь | Описание | Auth |
|---|---|---|
| `/recipes` | Список опубликованных рецептов (сетка) | Публичная |
| `/users/:userId` | Публичный профиль пользователя | Публичная |

**Fix (feat/public-user-profiles):** `getMe` использует нативный `fetch` вместо `apiJson`, чтобы 401 не вызывал `window.location.href = '/login'` на публичных страницах.

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
5. ~~Recipes list.~~ ✓
6. ~~Recipe details.~~ ✓
7. ~~Recipe create/edit.~~ ✓
8. ~~Категории + фильтрация + admin UI.~~ ✓
9. ~~Ингредиенты и шаги приготовления.~~ ✓
10. Layout.
10. Profile.
10. ~~Likes, favorites.~~ ✓
11. ~~Comments.~~ ✓
11. ~~Public user profiles, recipe card redesign, author display.~~ ✓
11. Meal plan.
12. Shopping list.
13. Moderation UI.
14. Admin UI.
15. UI polish, accessibility, performance.
