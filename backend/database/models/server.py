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
from sqlalchemy.orm import relationship

class Server(Base):
    """
    Represents a server in the Servers table.
    """
    __tablename__ = "Server"

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())

    owner_uuid = Column(Uuid, nullable=False)
    
    subusers = relationship("Subuser", backref="server", primaryjoin="Server.uuid == Subuser.uuid")

    node_uuid = Column(Uuid, nullable=False)
    chicken_uuid = Column(Uuid, nullable=False)

    database_limit = Column(Integer, nullable=False, default=0)
    backups_limit = Column(Integer, nullable=False, default=0)

    server_type = Column(Integer, nullable=False)

    installed = Column(Boolean, nullable=False, default=False)
