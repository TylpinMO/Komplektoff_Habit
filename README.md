# Komplektoff Habit

[![Проверки](https://github.com/TylpinMO/Komplektoff_Habit/actions/workflows/ci.yml/badge.svg)](https://github.com/TylpinMO/Komplektoff_Habit/actions/workflows/ci.yml)

Трекер привычек из трёх частей: Telegram-бот принимает быстрые отметки, FastAPI хранит данные, а панель на React показывает недельный ритм и серии.

[Открыть демонстрацию](https://komplektoff-habit.vercel.app)

## Что реализовано

- интерактивная адаптивная панель;
- отметка выполнения и добавление привычек;
- демонстрационный режим для публичной версии без доступа к базе;
- подключение к API через `VITE_BACKEND_URL`;
- регистрация пользователей, привычки, ежедневные отметки и статистика;
- защита от повторной отметки одной привычки в течение дня;
- Telegram-команды на aiogram;
- отдельные автоматические проверки frontend и backend.

## Структура

```text
frontend/  React + Vite
backend/   FastAPI + SQLModel + SQLite
bot/       aiogram + HTTP-клиент
```

## Быстрый запуск

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm ci
VITE_BACKEND_URL=http://127.0.0.1:8000 npm run dev
```

Bot:

```bash
pip install -r bot/requirements.txt
cp .env.example .env
python bot/bot.py
```

Основные переменные окружения:

| Переменная | Назначение | Значение по умолчанию |
|---|---|---|
| `TELEGRAM_TOKEN` | токен Telegram-бота | обязательна для бота |
| `BACKEND_URL` | адрес FastAPI для бота | `http://127.0.0.1:8000` |
| `DATABASE_URL` | строка подключения SQLModel | `sqlite:///./data.db` |
| `VITE_BACKEND_URL` | адрес API для frontend | демонстрационный режим |

## Проверка

```bash
cd frontend && npm test
python -m unittest discover -s backend/tests -v
```

## Деплой frontend на Vercel

В корне уже находится `vercel.json`. Vercel устанавливает зависимости из `frontend/`, запускает production build и публикует `frontend/dist`.

Для демонстрационной версии переменные окружения не нужны. Чтобы подключить публичный API, добавьте `VITE_BACKEND_URL` в настройках проекта Vercel и выполните новый deploy.

## Лицензия

MIT
