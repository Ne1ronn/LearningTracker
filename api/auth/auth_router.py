from database.setup import SessionDep
from fastapi import APIRouter
from schemas.user_schema import UserAddSchema, UserLoginSchema
from api.auth.register import register, login, get_user_by_username
router = APIRouter(tags=["Authentification"])

@router.post("/register")
async def register_user(session: SessionDep, user: UserAddSchema):
    await register(session, user)
    return {"User created successfully": True}

@router.post("/login")
async def login_user(session: SessionDep, user: UserLoginSchema):
    return await login(session, user)

@router.get("/user/{username}")
async def get_user(session: SessionDep, username: str):
    return await get_user_by_username(session, username)