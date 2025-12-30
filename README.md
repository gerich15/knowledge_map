# Knowledge Map - Карта знаний

Социальная сеть для визуализации и отслеживания личного прогресса в различных областях знаний.

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)

### Установка с помощью Docker

1. **Клонируйте репозиторий**

git clone <repository-url>
cd knowledge_map
Настройте переменные окружения

bash
cp .env.example .env
# Отредактируйте .env файл при необходимости
Запустите приложение

bash
docker-compose up -d
Примените миграции и создайте суперпользователя

bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py create_sample_data
Откройте в браузере

Приложение: http://localhost:8000

Админка: http://localhost:8000/admin

Локальная установка (без Docker)
Установите PostgreSQL

bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
Создайте базу данных

sql
CREATE DATABASE knowledge_map;
CREATE USER knowledge_user WITH PASSWORD 'knowledge_password';
GRANT ALL PRIVILEGES ON DATABASE knowledge_map TO knowledge_user;
Установите зависимости

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
Настройте переменные окружения

bash
cp .env.example .env
# Отредактируйте .env, укажите свои настройки БД
Запустите миграции

bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_sample_data
Запустите сервер

bash
python manage.py runserver
📁 Структура проекта
text
knowledge_map/
├── config/              # Настройки Django
├── api/                 # DRF API endpoints
├── users/               # Пользователи и аутентификация
├── branches/            # Ветки знаний
├── posts/               # Посты на временной шкале
├── subscriptions/       # Система подписок
├── timeline/            # Временные шкалы
├── templates/           # HTML шаблоны
├── static/              # Статические файлы
└── docker-compose.yml   # Docker конфигурация
🎯 Основные возможности
🌳 Ветки знаний
Создание тематических веток (например, "Изучение Python", "Путешествия")

Иерархическая структура (родительские/дочерние ветки)

Настройка приватности

Цветовое кодирование

📝 Посты на временной шкале
Привязка к конкретной дате

Разные типы контента (текст, ссылки, изображения, код)

Черновики и публикации

Лайки и комментарии

👥 Социальные функции
Подписки на пользователей и отдельные ветки

Лента активности из подписок

Поиск пользователей и контента

Система уведомлений

📊 Временная шкала
Интерактивная визуализация прогресса

Группировка по годам, месяцам и веткам

Фильтрация и навигация

Экспорт данных

🔧 API Endpoints
Аутентификация
POST /api/auth/login/ - Получение JWT токенов

POST /api/auth/refresh/ - Обновление токена

POST /api/auth/register/ - Регистрация

Пользователи
GET /api/users/ - Список пользователей

GET /api/users/{username}/ - Профиль пользователя

GET /api/users/{username}/timeline_data/ - Данные временной шкалы

Ветки
GET /api/branches/ - Список веток

POST /api/branches/ - Создание ветки

GET /api/branches/{id}/posts/ - Посты в ветке

Посты
GET /api/posts/ - Список постов

POST /api/posts/ - Создание поста

POST /api/posts/{id}/like/ - Лайк поста

Подписки
GET /api/subscriptions/ - Мои подписки

POST /api/subscriptions/ - Создание подписки

🎨 Фронтенд технологии
Django Templates - Серверный рендеринг

HTMX - Динамические взаимодействия без JavaScript

Alpine.js - Клиентская интерактивность

Tailwind CSS - Стилизация

Font Awesome - Иконки

🐳 Docker Команды
bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f web

# Выполнение команд в контейнере
docker-compose exec web python manage.py shell

# Пересборка образов
docker-compose build --no-cache

# Очистка
docker-compose down -v
📈 Развертывание
Подготовка к продакшену
Настройте .env для продакшена

env
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://...
Соберите статику

bash
docker-compose exec web python manage.py collectstatic --noinput
Настройте Nginx/Apache для статических файлов

Включите SSL через Let's Encrypt

🤝 Участие в разработке
Форкните репозиторий

Создайте ветку для фичи (git checkout -b feature/amazing-feature)

Зафиксируйте изменения (git commit -m 'Add amazing feature')

Запушьте ветку (git push origin feature/amazing-feature)

Откройте Pull Request

📄 Лицензия
MIT License

🆘 Поддержка
Issues: https://github.com/yourusername/knowledge-map/issues

Email: support@knowledge-map.example.com

Документация: https://docs.knowledge-map.example.com

text

## 18. config/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/auth/', include('api.urls')),
    path('api/', include('api.urls')),
    
    # Apps
    path('', TemplateView.as_view(template_name='dashboard.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('users/', include('users.urls')),
    path('branches/', include('branches.urls')),
    path('posts/', include('posts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('timeline/', include('timeline.urls')),
    
    # Auth (for templates)
    path('auth/', include('rest_framework.urls')),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
