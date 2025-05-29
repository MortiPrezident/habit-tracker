from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from web.schemas import TokenData
from envparse import Env

env = Env()
env.read_envfile()


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = env.str("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return PWD_CONTEXT.verify(plain, hashed)


def create_access_token(chat_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(chat_id)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(chat_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(chat_id)}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    print("TOKEN:", token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        print("DECODE ERROR:", e)
        raise
    print("PAYLOAD:", payload)
    chat_id = payload.get("sub")
    return TokenData(chat_id=int(chat_id))
