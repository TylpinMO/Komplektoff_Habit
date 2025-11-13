from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(index=True)
    username: Optional[str]
    registered_at: Optional[str]


class Habit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    name: str


class Done(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    habit_id: int = Field(index=True)
    date: date
