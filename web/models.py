from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from web.database import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    chat_id = Column(Integer, nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    refresh_token = Column(String(512), nullable=True)


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200))

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", backref="user_habits")

    habit_tracking = relationship("HabitTracking", back_populates="habit")


class HabitTracking(Base):
    __tablename__ = "habit_tracking"

    id = Column(Integer, primary_key=True)
    alert_time = Column(TIMESTAMP(timezone=True), nullable=False)
    count = Column(Integer, default=0)

    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)

    habit = relationship("Habit", back_populates="habit_tracking")


