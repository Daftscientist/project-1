"""
This module contains the Allocation model.
"""

import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
# pylint: disable=import-error
from database.db import Base


class Allocation(Base):
    """
    Represents an allocation in the Allocations table.
    """

    __tablename__ = 'Allocations'

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Integer, nullable=False, primary_key=True, default=uuid.uuid4())
    server_uuid = Column(Integer, nullable=True, default=None)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    node_identifier = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now,
        onupdate=func.now
    )
