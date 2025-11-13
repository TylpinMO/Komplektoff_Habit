# Habit Tracker — бот, backend и SPA

Коротко: это проект для трекинга привычек — Telegram‑бот, FastAPI backend (SQLite) и простой React SPA (Vite).

## Что в репо

- `backend/` — FastAPI + SQLModel (сохраняет в `data.db` в корне)
- `bot/` — Telegram бот на aiogram, пушит данные в backend
- `frontend/` — Vite + React SPA (dev сервер для разработки)

## Требования

- Git
- Python 3.9+ (желательно в виртуальном окружении)
- Node.js 16+ и `npm`

## Быстрый старт (локально)

1. Клонируйте репозиторий:

```bash
git clone https://github.com/TylpinMO/Komplektoff_Habit.git my-habit-tracker
cd my-habit-tracker
```

2. Создайте виртуальное окружение и установите зависимости Python:

```bash
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
pip install -r bot/requirements.txt
```

3. Установите зависимости фронтенда:

```bash
cd frontend
npm install
cd ..
```

4. Создайте `.env` (скопируйте из примера) и заполните значения:

```bash
cp .env.example .env
```

> В `.env` обязательно: `TELEGRAM_TOKEN` (если хотите тестировать бот через Telegram). `BACKEND_URL` по умолчанию `http://127.0.0.1:8000`.

5. Запуск сервисов (рекомендуется — в трёх отдельных терминалах)

- Backend (dev, интерактивно — видно логи):

```bash
source venv/bin/activate
cd /path/to/my-habit-tracker
venv/bin/python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

- Frontend (dev):

```bash
cd frontend
VITE_BACKEND_URL=http://127.0.0.1:8000 npm run dev -- --port 5173 --host 127.0.0.1
```

- Bot (интерактивно, чтобы сразу видеть ответы):

```bash
cd /path/to/my-habit-tracker
source .env
venv/bin/python bot/bot.py
```

6. Запуск в фоне (если нужно, и вы не хотите блокировать терминал)

- Backend (фон):

```bash
cd /path/to/my-habit-tracker
venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 > backend.log 2>&1 & echo $!
```

- Frontend (фон):

```bash
cd frontend
VITE_BACKEND_URL=http://127.0.0.1:8000 nohup npm run dev -- --port 5173 --host 127.0.0.1 > ../frontend.log 2>&1 & echo $!
```

- Bot (фон):

```bash
cd /path/to/my-habit-tracker
source .env
nohup venv/bin/python bot/bot.py > bot.log 2>&1 & echo $!
```

7. Логи и отладка

- Backend: `tail -f backend.log` (или смотреть вывод uvicorn в интерактивном режиме)
- Frontend: `tail -f frontend.log`
- Bot: `tail -f bot.log`

8. Полезные curl‑команды для быстрого теста API

```bash
# список пользователей
curl http://127.0.0.1:8000/users

# зарегистрировать тестового пользователя
curl -X POST "http://127.0.0.1:8000/bot/register_user?telegram_id=123&username=test"

# добавить привычку
curl -X POST "http://127.0.0.1:8000/bot/add_habit?user_id=1&name=Read"

# отметить выполнение
curl -X POST "http://127.0.0.1:8000/bot/done?user_id=1&habit_id=1"
```
