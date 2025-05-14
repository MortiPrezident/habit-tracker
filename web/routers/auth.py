import jwt
from fastapi import APIRouter, HTTPException, status, Depends
from web.schemas import UserOut, UserCreate, Token, TokenRefresh, UserLogin
from web.models import User
from web.dependencies import get_current_user
from web.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from web.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, session: AsyncSession =  Depends(get_async_session)):
    existing = await session.execute(
        User.__table__.select().where(User.name == user_in.name)
    )
    if existing.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user alredy exists")

    user = User(
            name=user_in.name,
            chat_id=user_in.chat_id,
            password_hash=hash_password(user_in.password)
    )
    access  = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    user.refresh_token = refresh
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return Token(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer"
    )


@router.post("/token/refresh", response_model=Token)
async def refresh_token(
        token_in: TokenRefresh,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        data = decode_token(token_in.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid refresh token")

    user = await session.get(User, data.user_id)
    if not user or user.refresh_token != token_in.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    user.refresh_token = refresh
    session.add(user)
    await session.commit()

    return Token(access_token=access, refresh_token=refresh,  token_type="bearer")


@router.post("/login", response_model=Token)
async def login(
        user_in: UserLogin,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.name == user_in.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    user.refresh_token = refresh
    session.add(user)
    await session.commit()

    return Token(access_token=access, refresh_token=refresh,  token_type="bearer")



@router.get("/user/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user