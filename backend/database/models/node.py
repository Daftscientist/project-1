"""
This module contains the Server model.
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

class Node(Base):
    """
    Represents a node in the Node table.
    """
    __tablename__ = "Node"

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    endpoint_url = Column(String, nullable=False)
    api_version = Column(String, nullable=False, default="1.0")

