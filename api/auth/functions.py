import uuid

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from datetime import datetime, timedelta
from database.setup import SessionDep
import os

from models.refresh_token_model import RefreshTokenModel

ACCESS_SECRET_KEY = os.environ["ACCESS_SECRET_KEY"]
REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain, password):
    return password_hash.verify(plain, password)

def create_access_token(username: str, role: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username,
               "role": role,
               "type": "access",
               "exp": expire}
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

async def create_refresh_token(session: SessionDep, user_id: int):
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {"sub": str(user_id),
               "jti": jti,
               "type": "refresh",
               "exp": expire}

    token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    db_token = RefreshTokenModel(
        jti=jti,
        user_id=user_id,
        expires_at=expire,
        revoked=False
    )

    session.add(db_token)
    await session.commit()

    return token