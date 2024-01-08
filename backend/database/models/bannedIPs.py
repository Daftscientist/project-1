from sqlalchemy import Column, Integer, String, Uuid, DateTime
import uuid
from database.db import Base
from sqlalchemy.sql import func
import datetime

class BannedIPs(Base):
    __tablename__ = 'User'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    banned_at = Column(DateTime, nullable=False, default=datetime.datetime.now())
    ip_of_admin = Column(String(255), nullable=False, default=None)
    ip = Column(String(255), nullable=False, default=None)
    reason = Column(String(255), nullable=False, default=None)

