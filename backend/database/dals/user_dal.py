"""
This module provides functionality for managing users in the database.
"""
import datetime
from typing import List, Optional

from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session
# pylint: disable=import-error
from database.models.user import User

class UsersDAL():
    """Data Access Layer for managing users in the database."""
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_user(
        self, username: str,
        email: str, password: str,
        latest_ip: str, signup_ip: str
    ):
        """
        Creates a new user.

        Args:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
            latest_ip (str): The latest IP address of the user.
            signup_ip (str): The IP address used during signup.

        Returns:
            None
        """
        new_user = User(
            username=username,
            email=email,
            password=password,
            latest_ip=latest_ip,
            signup_ip=signup_ip
        )
        self.db_session.add(new_user)
        await self.db_session.flush()

    async def get_user_by_uuid(self, uuid: int) -> User:
        """
        Returns the user with the given uuid.

        Args:
            uuid (int): The UUID of the user.

        Returns:
            User: The user object with the given UUID.
        """

        q = await self.db_session.execute(select(User).where(User.uuid == uuid))
        return q.scalars().first()

    async def get_user_by_email(self, email: str) -> User:
        """
        Retrieve a user from the database based on their email.

        Args:
            email (str): The email of the user to retrieve.

        Returns:
            User: The user object corresponding to the given email, or None if no user is found.
        """

        q = await self.db_session.execute(select(User).where(User.email == email))
        return q.scalars().first()

    async def get_all_users(self) -> List[User]:
        """
        Retrieves all users from the database.

        Returns:
            A list of User objects representing all users in the database.
        """

        q = await self.db_session.execute(select(User).order_by(User.identifier))
        return q.scalars().all()

    async def update_user(
            self,
            uuid: int,
            username: Optional[str] = None,
            email: Optional[str] = None,
            password: Optional[str] = None,
            avatar: Optional[str] = None,
            last_login: Optional[datetime.datetime] = None,
            latest_ip: Optional[str] = None,
            signup_ip: Optional[str] = None,
            max_sessions: Optional[str] = None,
            google_account_identifier: Optional[str] = None,
            discord_account_identifier: Optional[str] = None
        ):
        """
        Updates the user with the given uuid.

        Args:
            uuid (int): The unique identifier of the user.
            username (str, optional): The new username for the user. Defaults to None.
            email (str, optional): The new email for the user. Defaults to None.
            password (str, optional): The new password for the user. Defaults to None.
            avatar (str, optional): The new avatar for the user. Defaults to None.
            last_login (datetime.datetime, optional): The new last login timestamp for the user.
                Defaults to None.
            latest_ip (str, optional): The new latest IP address for the user. Defaults to None.
            signup_ip (str, optional): The new signup IP address for the user. Defaults to None.
            max_sessions (str, optional): The new maximum number of sessions for the user.
                Defaults to None.
            google_account_identifier (str, optional): The Google account identifier for the user.
                Defaults to None.
            discord_account_identifier (str, optional): The Discord account identifier for the user.
                Defaults to None.
        """

        q = update(User).where(User.uuid == uuid)
        if username:
            q = q.values(username=username)
        if email:
            q = q.values(email=email)
        if password:
            q = q.values(password=password)
        if avatar:
            q = q.values(avatar=avatar)
        if last_login:
            q = q.values(last_login=last_login)
        if latest_ip:
            q = q.values(latest_ip=latest_ip)
        if signup_ip:
            q = q.values(signup_ip=signup_ip)
        if max_sessions:
            q = q.values(max_sessions=max_sessions)
        if google_account_identifier:
            q = q.values(google_account_identifier=google_account_identifier)
        if discord_account_identifier:
            q = q.values(discord_account_identifier=discord_account_identifier)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)

    async def check_if_user_exists(self, username: str, email: str) -> bool:
        """
        Checks if a user with the given username or email exists.

        Args:
            username (str): The username to check.
            email (str): The email to check.

        Returns:
            bool: True if a user with the given username or email exists, False otherwise.
        """
        q = await self.db_session.execute(select(User).where(User.username == username))
        if q.scalars().first():
            return True
        q = await self.db_session.execute(select(User).where(User.email == email))
        if q.scalars().first():
            return True
        return False

    async def check_if_user_exists_email(self, email: str) -> bool:
        """
        Checks if a user with the given email exists.

        Args:
            email (str): The email to check.

        Returns:
            bool: True if a user with the given email exists, False otherwise.
        """
        q = await self.db_session.execute(select(User).where(User.email == email))
        if q.scalars().first():
            return True
        return False

    async def check_if_user_exists_username(self, username: str) -> bool:
        """
        Checks if a user with the given username or email exists.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if a user with the given username or email exists, False otherwise.
        """
        q = await self.db_session.execute(select(User).where(User.username == username))
        if q.scalars().first():
            return True
        return False

    async def delete_user(self, uuid: int):
        """
        Deletes the user with the given uuid.

        Parameters:
        - uuid (int): The unique identifier of the user to be deleted.
        """
        await self.db_session.execute(delete(User).where(User.uuid == uuid))
        await self.db_session.flush()
