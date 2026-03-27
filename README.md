# Сервис авторизации по номеру телефона

## Описание проект.
Сервис авторизации на Django, DRF. Предоставляет функционал аутентификации пользователей с реферальной системой.
Сервис позволяет пользователям регистрироваться при помощи мобильного номера телефона и управлять инвайт-кодами для реферальной системы.

## Функционал

- Авторизация по номеру телефона 
- Автоматическая генерация инвайт-кода
- Реферальная система
- REST API интерфейс
- Документация Swagger и Redoc 

## Технологии проекта

- Python 3.10+
- Django
- Django REST Framework
- PostgreSQL (база данных)
- Redis (кэширование)
- Docker и Docker Compose (контейнеризация)
- Swagger и Redoc /OpenAPI для документации

## Разработка 

Разработано приложение `users`. В модели пользователя реализованы поля:
- `phone_number` - номер телефона пользователя
- `invite_code` - инфайт-код
- `referral_code` - реферальный код

### Представления:
- `RequestCodeView` - запрос кода подтверждения 
- `VerifyCodeView` - верификация кода
- `ProfileView` - просмотр профиля
- `ActivateReferralCodeView` - активация реферального кода
- `LogoutProfileView` - выход из профиля

### Реализованы сервисы:
- `SMSService` - сервис для работы с СМС
- `AuthService` - сервис аутентификации
- `ReferralService` - сервис для реферальной системы

### Добавлена валидация:
- `validate_phone_number` - валидатор для номера телефона 
- `validate_verification_code` - валидатор кода подтверждения
- `validate_referral_code` - валидатор реферального кода

## SMSAero

Отправка кода подтверждения по СМС была реализована через сервис `SMSAero`.

- Зарегистрироваться на https://smsaero.ru/integration/api/
- Прочитать документацию https://smsaero.ru/integration/class/python/
- Добавить логин и API ключ из личного кабинета

### Тестирование
Для тестирования API в проект добавлена Postman коллекция в файле `AuthorizationServiceAPI.postman_collection.json`

Так же в проекте реализованы разные тесты функционала
- Запустить тесты `python manage.py test`
- Просмотр покрытия тестами `coverage report`

## Установка:
1. Клонируйте репозиторий
- `git@github.com:qewkus/Authorization_Service.git`

2. Создайте виртуальное окружение:
- `python -m venv venv`

3. Активируйте виртуальное окружение:
- `venv\Scripts\activate` - для Windows
- `source venv/bin/activate` - для macOS/Linux

4. Установите зависимости
- `pip install -r requirements.txt`   

5. Создайте файл .env на основе .env.sample

6. Docker контейнеризация
- Запустить сборку контейнеров - `docker-compose up -d --build`
- Остановить и удалить - `docker compose down`

## Документация
- Для Swagger UI - `http://127.0.0.1:8000/swagger/`
- Для Redoc - `http://127.0.0.1:8000/redoc/`