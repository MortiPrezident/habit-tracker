from fastapi import FastAPI, Depends, HTTPException, status
from web.database import get_async_session, AsyncSession
from sqlalchemy.future import select
from web.models import User
from sqlalchemy import text

app = FastAPI()

@app.get("/login")
async def hello():
    return "hello"

