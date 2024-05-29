"""
This module contains the mfa backup codes model.
"""
import datetime
import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    Uuid,
    DateTime,
    Boolean,
)
# pylint: disable=import-error
from database.db import Base

class Mfa_backup_codes(Base):
    """
    Represents a set of mfa backup codes in the Mfa backup codes table.
    """
    __tablename__ = "Mfa_backup_codes"

    identifier = Column(Integer, nullable=False, autoincrement=True, primary_key=True, unique=True)
    owner_uuid = Column(Uuid, nullable=False)
    code = Column(String, nullable=False, unique=True)
    
