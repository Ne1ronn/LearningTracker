from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
from dotenv import load_dotenv
import os

load_dotenv()
config = context.config
fileConfig(config.config_file_name)

import models
from models.base import Base

target_metadata = Base.metadata

DATABASE_URL_ALEMBIC = os.environ["DATABASE_URL_ALEMBIC"].replace(
    "postgresql://", "postgresql+psycopg://"
)


def run_migrations_online():
    engine = create_engine(
        str(DATABASE_URL_ALEMBIC),
        poolclass=None,
    )

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
