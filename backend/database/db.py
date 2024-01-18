"""
This module contains the database configuration and initialization code.
"""

#import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sanic.log import logger

#DATABASE_URL = os.getenv("APPLICATION_CONFIG_COOKIE_SESSION_NAME")

#print(DATABASE_URL)

engine = create_async_engine('sqlite+aiosqlite:///./test.db', future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def init(dev=False):
    """
    Initializes the database.

    Args:
        dev (bool): If True, drops all tables and recreates them. Default is False.

    Returns:
        None
    """
    async with engine.begin() as conn:
        if dev:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logger.info('Tables dropped and created')
        logger.info('Database initialized')
