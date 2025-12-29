import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Self

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base


class PlanaDB:
    """
    Singleton class for database connection and session management.
    """

    _instance = None
    base = declarative_base()
    engine: AsyncEngine = None
    async_session: async_sessionmaker[AsyncSession] = None

    def __new__(cls, url: str):
        if cls._instance is None:
            cls._instance = super(PlanaDB, cls).__new__(cls)
            cls._instance.engine = create_async_engine(
                url,
                echo=False,
                future=True,
                pool_pre_ping=True,
            )
            cls._instance.async_session = async_sessionmaker(
                cls._instance.engine, expire_on_commit=False, class_=AsyncSession
            )
        return cls._instance

    @classmethod
    @asynccontextmanager
    async def get_session(cls):
        """
        Provides an asynchronous database session.
        """
        async with cls._instance.async_session() as session:
            yield session

    @classmethod
    async def create_all(cls):
        """Create all tables"""
        db = cls._instance
        if db.engine is None or db.async_session is None:
            logger.error(
                "Engine or async session is not ready, please initialize the database first with init_db()"
            )
            sys.exit(1)

        async with db.engine.begin() as conn:
            await conn.run_sync(PlanaDB.base.metadata.create_all)

    @classmethod
    async def drop_all(cls):
        """Drop all tables"""
        db = cls._instance
        if db.engine is None or db.async_session is None:
            logger.error(
                "Engine or async session is not ready, please initialize the database first with init_db()"
            )
            sys.exit(1)

        logger.info("Dropping all tables...")

        try:
            async with db.engine.begin() as conn:
                await conn.run_sync(PlanaDB.base.metadata.drop_all)

        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise

    @classmethod
    async def recreate_all(cls):
        """Drop and recreate all tables"""
        await cls.drop_all()
        await cls.create_all()

    @classmethod
    def init_db(cls, connection_string: str = None) -> Self:
        """
        # Initialize the database singleton
        """
        logger.info("Initializing Plana Database...")

        try:
            db = cls(connection_string)
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            sys.exit(1)
        return db


def get_database_url() -> str:
    """
    Get the database URL from environment variables.
    """
    from dotenv import load_dotenv

    load_dotenv()

    db_name = os.getenv("PLANA_DB_NAME")
    user = os.getenv("PLANA_USER")
    password = os.getenv("PLANA_PASSWORD")
    url = os.getenv("DATABASE_URL")

    return f"postgresql+asyncpg://{user}:{password}@{url}/{db_name}"


# Utility functions
def validate_kwargs(kwargs: dict, class_instance: Any) -> bool:
    """
    Validates that the keys in kwargs are valid attributes of the class instance.
    """
    for key in kwargs:
        if not hasattr(class_instance, key):
            raise ValueError(f"Invalid key: {key}")
    return True
