import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from web.database import get_async_session
from web.models import User
from web.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_async_session)):
    try:
        token_data = decode_token(token)
    except jwt.PyJWTError:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token" )

    user = await  session.get(User, token_data.user_id)

    if not user:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not user")
    return user

