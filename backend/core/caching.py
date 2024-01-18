
"""
This module provides functions for caching user information in the application.
"""

import pickle
from sanic import Sanic
from sanic import Unauthorized
import sanic
# pylint: disable=import-error
# - to fix
from database.models.user import User
from core.cookies import get_session_id

import aiosqlite

class Cache:
    """
    A caching manager that stores cache in a SQLite database.

    Attributes:
        db_path (str): The path to the SQLite database file.
    """

    def __init__(self, db_path: str):
        """
        Initializes the session manager.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path

    async def async__init__(self):
        """
        Initializes the caching object and creates the Sessions table if it doesn't exist.

        Args:
            self (Caching): The Caching object.

        Returns:
            None
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS Sessions (
                    user_identifier TEXT PRIMARY KEY,
                    data BLOB,
                    cached_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            await db.commit()

    async def add(self, user_info) -> None:
        """
        Add user information to the cache.

        Args:
            user_info: The user information to be added.

        Returns:
            None
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO Sessions (user_identifier, data) VALUES (?, ?)',
                (user_info.uuid.hex, pickle.dumps(user_info, pickle.HIGHEST_PROTOCOL,))
            )
            await db.commit()

    async def get(self, request: sanic.Request) -> User:
        """
        Retrieve a user object from the cache based on the session ID.

        Args:
            request (sanic.Request): The request object containing the session ID.

        Returns:
            User: The user object retrieved from the cache.

        Raises:
            Unauthorized: If authentication is required or the session ID is invalid.
        """
        app = Sanic.get_app()
        uuid = await app.ctx.session.get(get_session_id(request))

        if uuid is None:
            return Unauthorized("Authentication required.")

        async with aiosqlite.connect(self.db_path) as db:
            query = 'SELECT data FROM Sessions WHERE user_identifier = ?'
            params = (uuid.hex,)
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    return pickle.loads(row[0])

    async def update(self, user_info: User) -> None:
        """
        Update user information in the cache.

        Args:
            user_info (User): The updated user information.

        Returns:
            None
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO Sessions (user_identifier, data) '
                'VALUES (?, ?)',
                (user_info.uuid.hex, pickle.dumps(user_info, pickle.HIGHEST_PROTOCOL,))
            )
            await db.commit()

    async def remove(self, uuid: str) -> None:
        """
        Remove user information from the cache.

        Args:
            uuid (str): The UUID of the user to be removed.

        Returns:
            None
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions WHERE user_identifier = ?', (uuid.hex,))
            await db.commit()

    async def get_user(self, request: sanic.Request) -> dict:
        """
        Retrieve user information from the cache.

        Args:
            request (sanic.Request): The request object containing the session ID.

        Returns:
            dict: A dictionary containing the user information.

        """
        session_token = get_session_id(request)
        user = await self.get(request)
        return {
            'session_id': session_token,
            'identifier': user.identifier,
            'uuid': user.uuid,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar,
            'last_login': user.last_login,
            'latest_ip': user.latest_ip,
            'signup_ip': user.signup_ip,
            'max_sessions': user.max_sessions,
            'created_at': user.created_at,
            'google_account_identifier': user.google_account_identifier,
            'discord_account_identifier': user.discord_account_identifier
        }
