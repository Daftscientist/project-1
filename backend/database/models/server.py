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

class Server(Base):
    """
    Represents a server in the Servers table.
    """
    __tablename__ = "Server"

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    node_identifier = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())

    cpu_limit = Column(Integer, nullable=False)
    memory_limit = Column(Integer, nullable=False)
    disk_limit = Column(Integer, nullable=False)
    swap_limit = Column(Integer, nullable=False, default=0)
    io_limit = Column(Integer, nullable=False, default=0)
    threads_limit = Column(Integer, nullable=False, default=0)

    database_limit = Column(Integer, nullable=False, default=0)
    backups_limit = Column(Integer, nullable=False, default=0)

    server_type = Column(Integer, nullable=False)

    installed = Column(Boolean, nullable=False, default=False)
