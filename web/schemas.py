from pydantic import BaseModel
from typing import Optional
from datetime import time


class UserCreate(BaseModel):
    name: str
    password: str
    chat_id: int


class Token(BaseModel):
    access_token: str
    refresh_token: str
    chat_id: int


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    chat_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    name: str
    chat_id: int
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    name: str
    password: str


class HabitCreate(BaseModel):
    name: str
    description: str
    alert_time: time


class HabitSynchronizationOut(BaseModel):
    habit_id: int
    chat_id: int
    habit_name: str
    time_str: time

    model_config = {"from_attributes": True}


class HabitsSynchronizationOut(BaseModel):
    habits: list[HabitSynchronizationOut]

    model_config = {"from_attributes": True}


class HabitOut(BaseModel):
    id: int
    name: str
    description: str
    alert_time: time
    count: int
    user_id: int
    completed: bool = False

    model_config = {"from_attributes": True}


class HabitsOut(BaseModel):
    habits: list[HabitOut]

    model_config = {"from_attributes": True}


class HabitEdit(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    alert_time: Optional[time] = None

    model_config = {"from_attributes": True}
