from sqlalchemy import Column, Integer, String, ForeignKey, TIME, BigInteger, BOOLEAN
from web.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    chat_id = Column(BigInteger, nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    refresh_token = Column(String(512), nullable=True)


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200), default="")
    alert_time = Column(TIME, nullable=False)
    count = Column(Integer, default=0)
    completed = Column(BOOLEAN, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", backref="user_habits")
