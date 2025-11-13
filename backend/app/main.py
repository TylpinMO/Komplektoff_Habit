from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, select
from datetime import date, timedelta
from typing import List

from .database import engine, get_session
from .models import User, Habit, Done
from sqlmodel import Session

app = FastAPI(title="Habit Tracker API")

# Allow frontend dev server to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/bot/register_user")
def register_user(telegram_id: int, username: str = None):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
        if user:
            return {"id": user.id}
        user = User(telegram_id=telegram_id, username=username, registered_at=str(date.today()))
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id}


@app.post("/bot/add_habit")
def add_habit(user_id: int, name: str):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        habit = Habit(user_id=user_id, name=name)
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return {"id": habit.id}


@app.post("/bot/done")
def mark_done(user_id: int, habit_id: int):
    with Session(engine) as session:
        habit = session.get(Habit, habit_id)
        if not habit or habit.user_id != user_id:
            raise HTTPException(status_code=404, detail="Habit not found")
        today = date.today()
        done = Done(habit_id=habit_id, date=today)
        session.add(done)
        session.commit()
        return {"ok": True}


@app.get("/users")
def list_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return [
            {"id": u.id, "telegram_id": u.telegram_id, "username": u.username, "registered_at": u.registered_at}
            for u in users
        ]


@app.get("/users/by_telegram/{telegram_id}")
def get_user_by_telegram(telegram_id: int):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.telegram_id == telegram_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "telegram_id": user.telegram_id, "username": user.username, "registered_at": user.registered_at}


@app.get("/users/{user_id}/habits")
def user_habits(user_id: int):
    with Session(engine) as session:
        habits = session.exec(select(Habit).where(Habit.user_id == user_id)).all()
        out = []
        for h in habits:
            done_rows = session.exec(select(Done).where(Done.habit_id == h.id)).all()
            count = len(done_rows)
            out.append({"id": h.id, "name": h.name, "done_count": count})
        return out


@app.get("/users/{user_id}/stats")
def user_stats(user_id: int):
    with Session(engine) as session:
        habits_rows = session.exec(select(Habit).where(Habit.user_id == user_id)).all()
        habits_count = len(habits_rows)
        week_ago = date.today() - timedelta(days=7)
        done_rows = session.exec(
            select(Done).where(Done.date >= week_ago).join(Habit, Habit.id == Done.habit_id).where(Habit.user_id == user_id)
        ).all()
        done_count = len(done_rows)
        return {"habits": habits_count, "done_last_7_days": done_count}
