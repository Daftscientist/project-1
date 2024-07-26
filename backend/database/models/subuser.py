"""
This module contains the Subuser model.
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

class Subuser(Base):
    """
    Represents a subuser in the Subusers table.
    """
    __tablename__ = "Subuser"

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    
    server_uuid = Column(Uuid, nullable=False)

    
