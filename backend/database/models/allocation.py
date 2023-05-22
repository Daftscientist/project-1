from sqlalchemy import Column, Integer, String, Uuid, DateTime
import uuid
from database.db import Base
from sqlalchemy.sql import func


class Allocation(Base):
    __tablename__ = 'Allocation'

    identifier = Column(Integer, nullable=False, autoincrement=True)
    uuid = Column(Uuid, nullable=False, primary_key=True, default=uuid.uuid4())
    server_uuid = Column(Uuid, nullable=True, default=None)
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    node_identifier = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
