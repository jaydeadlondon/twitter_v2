# Twitter v2 - Корпоративный сервис микроблогов

Полнофункциональный бэкенд для корпоративного сервиса микроблогов с REST API, документацией Swagger и поддержкой PostgreSQL.

## 🚀 Особенности

- **REST API** с полной документацией Swagger
- **Аутентификация** через API ключи
- **PostgreSQL** база данных с миграциями
- **Docker Compose** для простого развертывания
- **Загрузка файлов** с поддержкой изображений
- **Unit тесты** с высоким покрытием
- **Типизация** с поддержкой mypy
- **Линтеры** для качества кода

## 📋 Функционал

### Основные возможности:
- ✅ Создание и удаление твитов
- ✅ Лайки и дизлайки твитов
- ✅ Подписки на пользователей
- ✅ Лента твитов по популярности
- ✅ Загрузка изображений к твитам
- ✅ Профили пользователей
- ✅ API документация

### API Endpoints:

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/tweets` | Создать твит |
| DELETE | `/api/tweets/<id>` | Удалить твит |
| GET | `/api/tweets` | Получить ленту твитов |
| POST | `/api/tweets/<id>/likes` | Лайкнуть твит |
| DELETE | `/api/tweets/<id>/likes` | Убрать лайк |
| POST | `/api/medias` | Загрузить изображение |
| POST | `/api/users/<id>/follow` | Подписаться на пользователя |
| DELETE | `/api/users/<id>/follow` | Отписаться от пользователя |
| GET | `/api/users/me` | Получить свой профиль |
| GET | `/api/users/<id>` | Получить профиль пользователя |

## 🛠 Технологии

- **Python 3.11+**
- **Flask** - веб-фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Flasgger** - Swagger документация
- **Docker & Docker Compose** - контейнеризация
- **pytest** - тестирование
- **mypy, flake8, black** - линтеры

## 🚀 Быстрый старт

### Запуск через Docker Compose (рекомендуется)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/jaydeadlondon/twitter_v2.git
   cd twitter_v2
   ```

2. **Запустите приложение:**
   ```bash
   docker-compose up -d
   ```

3. **Проверьте, что сервисы запущены:**
   ```bash
   docker-compose ps
   ```

4. **Откройте браузер:**
   - Фронтенд: http://localhost:5000
   - API документация: http://localhost:5000/api/docs

### Локальный запуск для разработки

1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Настройте PostgreSQL:**
   ```bash
   # Создайте базу данных
   createdb twitter_db
   
   # Создайте пользователя
   psql -c "CREATE USER twitter_user WITH PASSWORD 'twitter_password';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE twitter_db TO twitter_user;"
   ```

3. **Установите переменные окружения:**
   ```bash
   export FLASK_ENV=development
   export DATABASE_URL=postgresql://twitter_user:twitter_password@localhost:5432/twitter_db
   export SECRET_KEY=your-secret-key
   ```

4. **Запустите приложение:**
   ```bash
   python run.py
   ```

## 🧪 Тестирование

### Запуск тестов:
```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=app

# Конкретный тест
pytest tests/test_api.py::TestTweetAPI::test_create_tweet_success
```

### Линтеры:
```bash
# Проверка стиля кода
flake8 app tests

# Форматирование кода
black app tests

# Сортировка импортов
isort app tests

# Проверка типов
mypy app
```

## 🔑 API ключи для тестирования

После запуска приложения будут созданы тестовые пользователи с API ключами:

| Пользователь | API ключ | Email |
|--------------|----------|-------|
| alice | alice-key-123 | alice@example.com |
| bob | bob-key-456 | bob@example.com |
| charlie | charlie-key-789 | charlie@example.com |

## 📖 Использование API

### Пример создания твита:
```bash
curl -X POST http://localhost:5000/api/tweets \\
  -H "Content-Type: application/json" \\
  -H "api-key: alice-key-123" \\
  -d '{"tweet_data": "Мой первый твит!"}'
```

### Пример загрузки изображения:
```bash
curl -X POST http://localhost:5000/api/medias \\
  -H "api-key: alice-key-123" \\
  -F "file=@image.jpg"
```

### Пример получения ленты:
```bash
curl -X GET http://localhost:5000/api/tweets \\
  -H "api-key: alice-key-123"
```

## 🗄 Структура базы данных

### Таблицы:
- **users** - пользователи с API ключами
- **tweets** - твиты пользователей
- **follows** - подписки между пользователями
- **likes** - лайки твитов
- **media** - загруженные файлы

### Схема:
```sql
users (id, username, email, api_key, created_at)
tweets (id, user_id, content, created_at)
follows (id, follower_id, following_id, created_at)
likes (id, user_id, tweet_id, created_at)
media (id, tweet_id, filename, original_filename, content_type, file_size, created_at)
```

## 🔧 Конфигурация

### Переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `FLASK_ENV` | Окружение (development/production) | development |
| `DATABASE_URL` | URL базы данных PostgreSQL | см. config.py |
| `SECRET_KEY` | Секретный ключ Flask | генерируется |
| `UPLOAD_FOLDER` | Директория для загрузок | ./uploads |

## 📁 Структура проекта

```
twitter_v2/
├── app/
│   ├── __init__.py          # Flask приложение
│   ├── models.py            # Модели SQLAlchemy
│   ├── routes.py            # API endpoints
│   └── schemas.py           # Формы (не используется)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Настройки pytest
│   ├── test_models.py       # Тесты моделей
│   └── test_api.py          # Тесты API
├── static/                  # Фронтенд файлы
├── uploads/                 # Загруженные файлы
├── config.py                # Конфигурация
├── run.py                   # Точка входа
├── requirements.txt         # Зависимости Python
├── docker-compose.yml       # Docker Compose
├── Dockerfile              # Docker образ
├── init_db.sql             # Инициализация БД
└── README.md               # Документация
```

## 🐛 Отладка

### Логи Docker:
```bash
# Все сервисы
docker-compose logs -f

# Только веб-сервер
docker-compose logs -f web

# Только база данных
docker-compose logs -f db
```

### Подключение к базе данных:
```bash
# Через Docker
docker-compose exec db psql -U twitter_user -d twitter_db

# Локально
psql -h localhost -U twitter_user -d twitter_db
```

## 📄 Лицензия

MIT License

**Примечание:** Это демонстрационное приложение для корпоративной среды.