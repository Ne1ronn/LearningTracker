import os
import uuid
import jwt
from datetime import datetime, UTC, timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from .user_repo import get_user_by_id
from database.setup import SessionDep
from models import RefreshTokenModel

ACCESS_SECRET_KEY = os.environ["ACCESS_SECRET_KEY"]
REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_DAYS = 7
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def verify_refresh(session: SessionDep, token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(401, detail="Wrong token type")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(401, detail="Empty refresh token")

    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(401, detail="Invalid user id")

    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=401, detail="JTI not found")

    db_token = await session.get(RefreshTokenModel, jti)
    user = await get_user_by_id(session, user_id)

    if not db_token:
        raise HTTPException(404, detail="Token not found")
    if db_token.revoked:
        raise HTTPException(401, detail="Token has been revoked")
    if db_token.expires_at < datetime.now(UTC).replace(tzinfo=None):
        raise HTTPException(401, detail="Token has expired")
    if user is None:
        raise HTTPException(404, detail="User not found")
    if db_token.user_id != user.id:
        raise HTTPException(401, detail="Invalid user id")
    return {"user": user, "db_token": db_token}


def create_access_token(username: str, role: str):
    expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": username, "role": role, "type": "access", "exp": expire}
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(session: SessionDep, user_id: int):
    jti = str(uuid.uuid4())
    expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {"sub": str(user_id), "jti": jti, "type": "refresh", "exp": expire}

    token = jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    db_token = RefreshTokenModel(
        jti=jti, user_id=user_id, expires_at=expire, revoked=False
    )

    session.add(db_token)
    await session.commit()

    return token
