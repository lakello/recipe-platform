# Android

Android-приложение Recipe Platform — мобильный клиент платформы рецептов и планирования питания.

Приложение позволяет пользователям искать рецепты, просматривать инструкции приготовления, авторизоваться, сохранять избранное, планировать питание на неделю и работать со списком покупок с мобильного устройства.

## Назначение директории

В директории `android/` находится код Android-приложения:

- Kotlin-код;
- UI на Jetpack Compose;
- сетевой слой для Backend API;
- локальное хранилище;
- модели данных;
- экраны приложения;
- навигация;
- тесты;
- Gradle-конфигурация;
- настройки сборки debug/release.

## Технологический стек

Планируемый стек Android:

- Kotlin
- Jetpack Compose
- Android Jetpack
- Material 3
- Navigation Compose
- ViewModel
- Kotlin Coroutines
- Kotlin Flow
- Retrofit
- OkHttp
- kotlinx.serialization или Moshi
- Room
- DataStore
- Coil
- Hilt или Koin
- JUnit
- MockK
- Turbine
- Compose UI Tests

Опционально:

- Firebase Cloud Messaging для push-уведомлений.

## Ответственность Android-приложения

Android-клиент отвечает за:

- просмотр публичных рецептов;
- поиск рецептов;
- фильтрацию по категориям;
- просмотр страницы рецепта;
- регистрацию и вход;
- OAuth login через browser/custom tabs;
- отображение профиля пользователя;
- редактирование профиля;
- избранные рецепты;
- лайки;
- комментарии;
- подписки;
- недельный план питания;
- список покупок;
- отметку продуктов как купленных;
- базовую offline-поддержку;
- загрузку изображений;
- отображение уведомлений;
- обработку ошибок API;
- безопасное хранение пользовательской сессии.

## Предполагаемая структура

```text

android/

app/

src/

main/

java/

com/

recipeplatform/

app/

core/

network/

database/

datastore/

security/

ui/

navigation/

feature/

auth/

recipes/

profile/

favorites/

mealplan/

shoppinglist/

notifications/

settings/

domain/

model/

repository/

usecase/

data/

remote/

local/

mapper/

repository/

res/

test/

androidTest/

build.gradle.kts

build.gradle.kts

settings.gradle.kts

gradle.properties

README.md
```

Структура может быть адаптирована, но желательно сохранять разделение на:

- `core`;
- `feature`;
- `domain`;
- `data`.

## Основные экраны

### Публичные экраны

- Splash screen;
- Onboarding, если будет добавлен;
- Главная;
- Список рецептов;
- Поиск;
- Фильтры;
- Детальная страница рецепта;
- Публичный профиль автора;
- Login;
- Register.

### Экраны пользователя

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

### Возможные экраны модерации

Для первого этапа модерацию можно оставить только в web/admin-интерфейсе.

Позже Android может поддерживать:

- список жалоб;
- просмотр жалобы;
- быстрые действия модератора.

## Навигация

Примерная структура navigation graph:

```
splash
auth
  login
  register
  oauth-callback

main
  home
  recipes
  recipe-details/{recipeId}
  search
  favorites
  meal-plan
  shopping-list
  profile
  settings
```

Для авторизованных экранов используется проверка сессии.

Если пользователь не авторизован, он перенаправляется на login.

## Работа с Backend API

Android-приложение использует тот же Backend API, что web и desktop-клиенты.

Базовый URL зависит от окружения:

```
local:      http://10.0.2.2:8000/api
dev:        https://api.dev.example.com/api
staging:    https://api.staging.example.com/api
production: https://api.example.com/api
```

`10.0.2.2` используется Android Emulator для доступа к localhost хостовой машины.

Пример Retrofit API

``` kotlin
interface RecipesApi {

@GET("recipes")

suspend fun getRecipes(

@Query("query") query: String? = null,

@Query("category") category: String? = null

): RecipesResponse

@GET("recipes/{id}")

suspend fun getRecipeById(

@Path("id") id: String

): RecipeDto

}
```

## Аутентификация

Backend выдаёт JWT access token и refresh token.

Android-клиент должен:

- выполнять login/register;
- хранить токены безопасно;
- добавлять access token в `Authorization` header;
- обновлять access token через refresh flow;
- выполнять logout;
- очищать локальные данные при logout.

Пример заголовка:

```
Authorization: Bearer <access-token>
```

## Безопасное хранение токенов

Для хранения сессии рекомендуется использовать:

- Jetpack DataStore;
- EncryptedSharedPreferences или Jetpack Security;
- Android Keystore для чувствительных данных.

Не рекомендуется хранить токены в обычных SharedPreferences без шифрования.

## OAuth

OAuth через Google и Яндекс выполняется через browser-based flow.

Ожидаемый сценарий:

1. 1.Пользователь нажимает кнопку входа через Google или Яндекс.
2. 2.Приложение открывает backend endpoint в браузере или Custom Tabs:

```
/api/auth/google/login
/api/auth/yandex/login
```

1. 1.Backend выполняет OAuth flow.
2. 2.После успеха backend возвращает пользователя в приложение через deep link.
3. 3.Android-приложение получает результат и обновляет состояние сессии.

Для этого нужно настроить deep links.

Пример:

```
recipeplatform://oauth/callback
```

## Работа с изображениями

Для загрузки фотографий рецептов и аватаров используется Object Storage через pre-signed URL.

Сценарий:

1. 1.Пользователь выбирает изображение.
2. 2.Android проверяет размер и MIME-type.
3. 3.Приложение запрашивает у backend pre-signed URL.
4. 4.Файл загружается напрямую в Object Storage.
5. 5.Приложение отправляет backend metadata файла.
6. 6.Backend сохраняет информацию в БД.
7. 7.Worker генерирует thumbnail.

Для отображения изображений используется Coil.

## Offline-поддержка

На первом этапе можно реализовать базовую offline-поддержку:

- кэширование просмотренных рецептов;
- кэширование избранного;
- кэширование текущего списка покупок;
- возможность отмечать продукты как купленные локально;
- синхронизация при восстановлении сети.

Для локального хранения используется Room.

## Локальная база данных

Room может хранить:

- кэш рецептов;
- избранные рецепты;
- текущий план питания;
- список покупок;
- user profile;
- pending sync actions.

Важно разделять:

- данные, полученные с сервера;
- локальные изменения, ожидающие синхронизации.

## Сетевой слой

Для сетевого слоя используются:

- Retrofit;
- OkHttp;
- Interceptors;
- kotlinx.serialization или Moshi.

Обязательные interceptors:

- `AuthorizationInterceptor`;
- `RefreshTokenInterceptor` или отдельный Authenticator;
- `RequestIdInterceptor`;
- `LoggingInterceptor` только для debug-сборок.

В production нельзя логировать токены и чувствительные данные.

## Конфигурация окружений

Рекомендуется поддерживать build flavors:

```
local
dev
staging
prod
```

Пример:

``` kotlin
productFlavors {

create("local") {

dimension = "environment"

buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/\"")

}



create("dev") {

dimension = "environment"

buildConfigField("String", "API_BASE_URL", "\"https://api.dev.example.com/api/\"")

}



create("staging") {

dimension = "environment"

buildConfigField("String", "API_BASE_URL", "\"https://api.staging.example.com/api/\"")

}



create("prod") {

dimension = "environment"

buildConfigField("String", "API_BASE_URL", "\"https://api.example.com/api/\"")

}

}
```

## Сборка

Debug-сборка:

``` bash
cd android

./gradlew assembleDebug
```

Release-сборка:

```
./gradlew assembleRelease
```

Сборка конкретного flavor:

``` bash
./gradlew assembleDevDebug

./gradlew assembleStagingRelease

./gradlew assembleProdRelease
```

## Запуск тестов

Unit tests:

```
./gradlew test
```

Instrumented tests:

```
./gradlew connectedAndroidTest
```

Проверка lint:

```
./gradlew lint
```

## Качество кода

Рекомендуемые проверки:

- Kotlin compiler checks;
- Android Lint;
- Detekt;
- Ktlint;
- unit tests;
- UI tests;
- dependency vulnerability scan.

В CI должны выполняться:

``` bash
./gradlew lint

./gradlew test

./gradlew assembleDebug
```

## Push-уведомления

Push-уведомления через Firebase Cloud Messaging можно добавить как расширение.

Возможные уведомления:

- новый комментарий;
- лайк рецепта;
- новый подписчик;
- новый рецепт автора;
- решение по жалобе;
- напоминание о плане питания.

Важно:

- не хранить Firebase secrets в Git;
- использовать разные конфигурации для dev/staging/prod;
- предусмотреть отключение уведомлений в настройках.

## Security

Основные требования безопасности:

- использовать HTTPS для dev/staging/prod;
- безопасно хранить токены;
- не логировать access token и refresh token;
- не логировать персональные данные;
- включать network security config;
- запрещать cleartext traffic в production;
- использовать certificate validation по умолчанию;
- проверять deep links;
- обрабатывать logout и очистку данных;
- минимизировать permissions;
- не хранить секреты в APK.

## Network Security Config

Для local-окружения может потребоваться cleartext traffic к `10.0.2.2`.

Для production cleartext traffic должен быть запрещён.

Пример идеи:

``` xml
<network-security-config>

<domain-config cleartextTrafficPermitted="false">

<domain includeSubdomains="true">example.com</domain>

</domain-config>

<domain-config cleartextTrafficPermitted="true">

<domain>10.0.2.2</domain>

</domain-config>

</network-security-config>
```

Реальная конфигурация должна быть разделена по build flavors.

## Observability

Android-приложение должно поддерживать базовую диагностику:

- логирование ошибок в debug;
- correlation ID для API-запросов;
- crash reporting можно добавить позже;
- performance monitoring можно добавить позже.

В production нельзя логировать чувствительные данные.

## UX-требования

Приложение должно обрабатывать:

- loading state;
- empty state;
- error state;
- offline state;
- unauthorized state;
- forbidden state;
- retry action;
- pull-to-refresh;
- pagination;
- optimistic updates для лайков и списка покупок.

## Accessibility

Нужно учитывать:

- content descriptions для иконок и изображений;
- достаточный контраст;
- масштабирование шрифтов;
- touch targets достаточного размера;
- поддержку TalkBack;
- понятные сообщения об ошибках.

## CI/CD

Android может участвовать в GitHub Actions pipeline.

На Pull Request:

- Gradle build;
- lint;
- unit tests;
- debug APK build.

На release pipeline:

- сборка release APK/AAB;
- подпись артефакта;
- публикация как GitHub artifact;
- опционально публикация во внутренний трек.

Секреты подписи release-сборки должны храниться только в GitHub Actions Secrets или другом защищённом хранилище.

## Статус

Android-приложение находится в разработке.

Приоритет реализации:

1. 1.Базовый Android-проект.
2. 2.Настройка Gradle.
3. 3.Build flavors.
4. 4.Navigation Compose.
5. 5.API client.
6. 6.Auth flow.
7. 7.Recipes list.
8. 8.Recipe details.
9. 9.Search.
10. 10.Favorites.
11. 11.Meal plan.
12. 12.Shopping list.
13. 13.Profile.
14. 14.Offline cache.
15. 15.Push notifications.
