from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models.user import User

class UsersDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(self, username: str, email: str, password: str):
        new_user = User(username=username, email=email, password=password)
        self.db_session.add(new_user)
        await self.db_session.flush()

    async def get_user_by_uuid(self, uuid: int) -> User:
        q = await self.db_session.execute(select(User).where(User.uuid == uuid))
        return q.scalars().first()

    async def get_all_users(self) -> List[User]:
        q = await self.db_session.execute(select(User).order_by(User.identifier))
        return q.scalars().all()

    async def update_user(self, uuid: int, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None, google_account_identifier: Optional[str] = None, discord_account_identifier: Optional[str] = None):
        q = update(User).where(User.uuid == uuid)
        if username:
            q = q.values(username=username)
        if email:
            q = q.values(email=email)
        if password:
            q = q.values(password=password)
        if google_account_identifier:
            q = q.values(google_account_identifier=google_account_identifier)
        if discord_account_identifier:
            q = q.values(discord_account_identifier=discord_account_identifier)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)