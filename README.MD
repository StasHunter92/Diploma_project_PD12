# Курс 7. Дипломная работа SkyPRO PD 12

______________________________________

### Данная курсовая работа представляет собой приложение 'Todolist'

<p align="left">
<img src="https://img.shields.io/badge/Python-3.10-green?style=flat-square&logo=appveyor" alt="Python 3.10">
<img src="https://img.shields.io/badge/Django-4.1.7-green?style=flat-square&logo=appveyor" alt="Python 3.10">
<img src="https://img.shields.io/badge/DRF-3.14.0-green?style=flat-square&logo=appveyor" alt="Python 3.10">
<img src="https://img.shields.io/badge/Docker-blue?style=flat-square&logo=appveyor" alt="Python 3.10">
<img src="https://img.shields.io/badge/PostgreSQL-blue?style=flat-square&logo=appveyor" alt="Python 3.10">
<img src="https://img.shields.io/badge/Pytest-blue?style=flat-square&logo=appveyor" alt="Python 3.10">
<img src="https://img.shields.io/docker/image-size/stashunter/todolist?style=flat-square" alt="Python 3.10">
</p>

______________________________________
**Приложение предназначено для удобного управления поставленными целями, сортируя их по категориям и доскам.
Также, к доскам, можно добавлять других участников для совместного использования приложением. Для быстрого доступа
к просмотру и добавлению целей можно использовать встроенный телеграм бот**

Приложение реализует такие возможности как:

1) Вход/регистрация через логин/пароль
2) Вход через Вконтакте
3) Создание целей
    - Выбор временного интервала цели с отображением кол-ва дней до завершения цели
    - Выбор категории цели (личные, работа, развитие, спорт и т. п.)
      с возможностью добавлять/удалять/обновлять категории
    - Выбор приоритета цели
    - Выбор статуса выполнения цели (в работе, выполнен, просрочен, в архиве)
4) Изменение целей
    - Изменение описания цели
    - Изменение статуса
    - Изменение приоритета
    - Изменение категории
5) Удаление целей
6) Комментирование целей
7) Поиск по названию цели
8) Фильтрация по статусу, категории, приоритету, году

______________________________________
**Используемый стек**

- Язык программирования: `Python 3.10`
- Фреймворк веб-приложений: `Django 4.1.7`
- Фреймворк для создания API: `Django Rest Framework 3.14.0`
- Веб-сервер: `Gunicorn 20.1.0`
- База данных: `PostgreSQL`
- Контейнеризация: `Docker`
- Плагин для автоматической генерации документации API: `drf-spectacular 0.26.1`
- Библиотека для работы с окружением: `django-environ 0.10.0`
- Библиотеки для сериализации и десериализации данных: `marshmallow 3.19.0`, `marshmallow-dataclass 8.5.13`
- Библиотека для аутентификации через социальные сети: `social-auth-app-django 5.2.0`
- Библиотека для создания конечных автоматов: `transitions 0.9.0`
- Фреймворк для тестирования: `pytest-django 4.5.2`
- Плагин для создания тестовых данных: `pytest-factoryboy 2.5.1`
- Плагин для расчёта покрытия кода тестами: `pytest-cov 4.0.0`

______________________________________
**Структура проекта**

- `bot/`: папка с приложением телеграм бота
- `core/`: папка с приложением управления пользователями
- `goals/`: папка с приложением управления досками и целями
- `diploma_project_pd12/settings.py`: файл с настройками проекта
- `diploma_project_pd12/urls.py`: файл с URL-адресами проекта
- `diploma_project_pd12/wsgi.py`: файл с конфигурацией WSGI-сервера
- `tests/`: папка с тестами
- `.env.deploy`: файл с настройками окружения
- `docker-compose_sample`: файл для запуска приложения через docker compose
- `Dockerfile`: файл для сборки Docker контейнера
- `manage.py`: файл для запуска Django команд
- `nginx.conf`: файл для настройки Nginx сервера
- `pyproject.toml`: файл для установки зависимостей через Poetry
- `pytest.ini`: файл для настройки тестов Pytest

______________________________________
**Установка и запуск приложения**

1) Клонируйте репозиторий
   ```sh
   git clone https://github.com/StasHunter92/Diploma_project_PD12.git
   ```
2) Переименуйте `docker-compose_sample.yml` в `docker-compose.yml`

3) Переименуйте `.env.deploy` в `.env` и присвойте необходимые значения переменным:
    - SECRET_KEY
    - В DATABASE_URL замените `$POSTGRES_USER`, `$POSTGRES_PASSWORD` и `$POSTGRES_DB` на соответствующие значения
      из `docker-compose.yml`
    - В VK_OAUTH2_KEY и VK_OAUTH2_SECRET замените `$VK_OAUTH2_KEY` и `$VK_OAUTH2_SECRET` на свои значения
    - В TG_TOKEN замените `$TG_TOKEN` на собственный ключ от бота

4) Запустите локальный сервер
   ```sh
   docker-compose up -d
   ```