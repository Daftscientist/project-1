from sqlalchemy import Column, Integer, String, Uuid, DateTime, URL
import uuid
from database.db import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'User'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), nullable=False)
    google_account_identifier = Column(String(255), nullable=True, default=None)
    discord_account_identifier = Column(String(18), nullable=True, default=None)
