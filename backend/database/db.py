"""
This module contains the database configuration and initialization code.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sanic.log import logger
import yaml
import os

def load_config(file_path: str = os.getcwd() + "/config.yml"):
    """
    Loads the configuration file.

    Args:
        file_path (str): The path to the configuration file. Default is "config.yaml".

    Returns:
        dict: The configuration dictionary.
    """
    with open(file_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

engine = create_async_engine(load_config()["database"]["url"], future=True, echo=True)
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
