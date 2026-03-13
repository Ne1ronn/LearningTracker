from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os

DATABASE_URL = os.environ["DATABASE_URL"].replace(
    "postgresql://", "postgresql+asyncpg://"
)

SQL_ECHO = os.getenv("SQL_ECHO")
echo = True if SQL_ECHO == "true" else False
engine = create_async_engine(
    str(DATABASE_URL),
    echo=echo,
)

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
