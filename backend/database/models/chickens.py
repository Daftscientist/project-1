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

class Chicken(Base):
    """
    Represents a node in the Chicken table.
    """
    __tablename__ = "Server"

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    name = Column(String, nullable=False)
    
    ## make a columnm called type that can only be one of the following values: OCI, SYSTEM, or VM
    type = Column(String, nullable=False)

    if type not in ['OCI', 'SYSTEM', 'VM']:
        raise ValueError('Invalid type')
    
    endpoint_url = Column(String, nullable=False)

    ## column to show if the chicken is suspended or not
    suspended = Column(Boolean, nullable=False, default=False)

    ## column to store the YML string of the Chicken
    yml = Column(String, nullable=False)