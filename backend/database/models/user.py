from sqlalchemy import Column, Integer, String, Uuid, DateTime
import uuid
from database.db import Base
from sqlalchemy.sql import func
import datetime

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'User'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    uuid = Column(Uuid, nullable=False, default=uuid.uuid4())
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True, default=None)
    last_login = Column(DateTime(timezone=True), nullable=True, default=None)
    latest_ip = Column(String(255), nullable=False, default=None)
    signup_ip = Column(String(255), nullable=False, default=None)
    max_sessions = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())
    google_account_identifier = Column(String(255), nullable=True, default=None)
    discord_account_identifier = Column(String(18), nullable=True, default=None)

