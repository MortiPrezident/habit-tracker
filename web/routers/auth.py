from fastapi import APIRouter, HTTPException, status, Depends
from web.schemas import UserOut, UserCreate, Token, TokenRefresh, UserLogin
from web.models import User
from web.dependencies import get_current_user, get_current_tokens
from web.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from web.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from sqlalchemy.future import select

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(
    user_in: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    existing = await session.execute(
        User.__table__.select().where(User.name == user_in.name)
    )
    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user alredy exists"
        )
    try:
        user = User(
            name=user_in.name,
            chat_id=user_in.chat_id,
            password_hash=hash_password(user_in.password),
        )
        session.add(user)
        await session.commit()

        access = create_access_token(user.chat_id)
        refresh = create_refresh_token(user.chat_id)

        user.refresh_token = refresh
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed"
        )

    return Token(access_token=access, refresh_token=refresh, chat_id=user.chat_id)


@router.post("/token/refresh", response_model=Token)
async def refresh_token(current_token: Token = Depends(get_current_tokens)):
    return current_token


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User).where(User.name == user_in.name))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    try:
        access = create_access_token(user.chat_id)
        refresh = create_refresh_token(user.chat_id)

        user.refresh_token = refresh
        session.add(user)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed"
        )
    return Token(access_token=access, refresh_token=refresh, chat_id=user.chat_id)


@router.get("/user/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
