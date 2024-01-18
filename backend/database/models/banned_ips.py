"""
This module contains the Banned Ips model.

"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime
# pylint: disable=import-error
from database.db import Base

class BannedIPs(Base):
    """
    Represents an BannedIp in the BannedIPs table.
    """

    __tablename__ = 'BannedIPs'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    banned_at = Column(DateTime, nullable=False, default=datetime.datetime.now())
    ip_of_admin = Column(String(255), nullable=False, default=None)
    ip = Column(String(255), nullable=False, default=None)
    reason = Column(String(255), nullable=False, default=None)
