"""
This module contains the User model.
"""
import datetime
import os
import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    Uuid,
    DateTime,
)
import yaml
# pylint: disable=import-error
from database.db import Base

def generate_uuid():
    """
    Generate a random UUID.

    Returns:
        str: A string representation of the generated UUID.
    """
    return str(uuid.uuid4())

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

class User(Base):
    """
    Represents a user in the users table.
    """

    __tablename__ = 'User'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    uuid = Column(Uuid, nullable=False, default=uuid.uuid4())
    username = Column(String, nullable=False) #
    email = Column(String, nullable=False) #
    password = Column(String, nullable=False) #
    avatar = Column(String, nullable=True, default=None) #
    last_login = Column(DateTime(timezone=True), nullable=True, default=None)
    latest_ip = Column(String(255), nullable=False, default=None)
    signup_ip = Column(String(255), nullable=False, default=None)
    max_sessions = Column(Integer, nullable=False, default=load_config()['session']['user_max_sessions'])
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())
    google_account_identifier = Column(String(255), nullable=True, default=None)
    discord_account_identifier = Column(String(18), nullable=True, default=None)
    #servers = relationship("Server", back_populates="user")
