import os
import jwt
from fastapi import HTTPException, status, Depends, Header
from jwt.exceptions import InvalidTokenError
from .token_service import ACCESS_SECRET_KEY, ALGORITHM, oauth2_scheme
from database.setup import SessionDep
from schemas.user_schema import TokenData
from .user_repo import get_user_by_username

BOT_SECRET = os.getenv("BOT_SECRET")

async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    credential_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credential_exceptions
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credential_exceptions
    user = await get_user_by_username(session, token_data.username)
    if user is None:
        raise credential_exceptions
    return user

async def require_role(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have enough permissions"
        )

async def verify_bot_secret(x_bot_secret: str = Header(...)):
    if x_bot_secret != BOT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid bot secret"
        )