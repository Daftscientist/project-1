from sqlalchemy import Column, Integer, String, Uuid, DateTime
import uuid
from database.db import Base
from sqlalchemy.sql import func
import datetime

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = 'User'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    uuid = Column(Uuid, nullable=True, default=uuid.uuid4())
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True, default=None)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())
    google_account_identifier = Column(String(255), nullable=True, default=None)
    discord_account_identifier = Column(String(18), nullable=True, default=None)

### "(sqlite3.IntegrityError) NOT NULL constraint failed: User.identifier\n[SQL: INSERT INTO \"User\" (identifier, uuid, username, email, password, avatar, created_at, google_account_identifier, discord_account_identifier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)]\n[parameters: (None, 'c647607e711748af84956d3d962440a2', 'leo', 'hello@leo-johnston.me', b'$2b$12$xX3TkEu8qnFELnaynfQj4e2TVXi.NJMtStYRsaI0KAfsYpHhVzcbq', None, '2023-08-12 12:50:19.338655', None, None)]\n(Background on this error at: https://sqlalche.me/e/20/gkpj)"