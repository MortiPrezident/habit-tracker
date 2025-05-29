import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from web.database import get_async_session
from web.models import User
from web.security import decode_token
from web.schemas import UserOut, Token
from web.security import create_access_token, create_refresh_token
from sqlalchemy.future import select


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_tokens(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    try:
        data = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid refresh token")
    query = await session.execute(select(User).where(User.chat_id == data.chat_id))
    user = query.scalar_one_or_none()

    if not user or user.refresh_token != token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    try:
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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        token_data = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    query = await session.execute(
        select(User).where(User.chat_id == token_data.chat_id)
    )
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not user")
    return UserOut(id=user.id, name=user.name, chat_id=user.chat_id)
