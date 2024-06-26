"""
This module provides functionality for managing sessions.
"""
import pickle
import uuid
import time
import aiosqlite

class SessionManager:
    """
    Manages sessions for the application.
    """
    def __init__(self, db_path: str):
        """
        Initializes the session manager.

        Args:
            db_path (str): The path to the database file.
        """
        self.db_path = db_path

    async def async__init__(self):
        """
        Asynchronously initializes the session manager.

        This method creates the 'Sessions' table in the database if it doesn't exist,
        and performs session cleanup to remove expired sessions.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS Sessions (
                    session_token TEXT PRIMARY KEY,
                    uuid TEXT,
                    creation_ip TEXT,                
                    expiry INTEGER,
                    authenticating_currently_using_two_factor_authentication BOOLEAN DEFAULT FALSE,
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            await db.commit()
            await self.session_cleanup()

    async def change_twofactor_auth_state(self, session_token: str, state: bool) -> None:
        """
        Changes the two-factor authentication state of a session.

        Args:
            session_token (str): The session token.
            state (bool): The new two-factor authentication state.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE Sessions SET authenticating_currently_using_two_factor_authentication = ? WHERE session_token = ?',
                (state, session_token)
            )
            await db.commit()
    
    async def get_twofactor_auth_state(self, session_token: str) -> bool:
        """
        Returns the two-factor authentication state of a session.

        Args:
            session_token (str): The session token.

        Returns:
            bool: True if the session is currently authenticating using two-factor authentication, False otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT authenticating_currently_using_two_factor_authentication FROM Sessions WHERE session_token = ?', (session_token,)) as cursor:
                row = await cursor.fetchone()
                print(row)
                if row is not None:
                    if row[0] == 1:
                        return True
                    return False
                return False

    async def get_all_users(self) -> list[str]:
        """
        Returns all users in the cache.

        Returns:
            list[str]: A list of user UUIDs.
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT uuid FROM Sessions') as cursor:
                return list(set([row for row in await cursor.fetchall()]))

    async def session_cleanup(self) -> None:
        """
        Removes all expired sessions from the database.

        This method is responsible for deleting sessions that have expired.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions WHERE expiry <= ?', (time.time(),))
            await db.commit()

    async def add(self, session_token: str, user_uuid: str, creation_ip: str, expiry: int) -> None:
        """
        Adds a session to the cache.

        Args:
            session_token (str): The session token.
            user_uuid (str): The UUID of the user.
            creation_ip (str): The IP address where the session was created.
            expiry (int): The Unix timestamp indicating the session expiry.

        Raises:
            ValueError: If the expiry is not a future Unix timestamp.
        """
        if expiry <= time.time():
            raise ValueError("Expiry must be a future Unix timestamp.")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR REPLACE INTO Sessions (session_token, uuid, creation_ip, expiry) '
                'VALUES (?, ?, ?, ?)',
                (session_token, user_uuid.hex, creation_ip, expiry)
            )
            await db.commit()

    async def check_session_token(self, session_token: str) -> bool:
        """
        Returns whether a session token is valid.

        Args:
            session_token (str): The session token.

        Returns:
            bool: True if the session token is valid, False otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            query = '''
                SELECT expiry
                FROM Sessions
                WHERE session_token = ?
                ORDER BY created_at ASC
            '''
            async with db.execute(query, (session_token,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    expiry = row[0]
                    if expiry > time.time():
                        return True
                await self.delete(session_token)
                return False

    async def get(self, session_token: str) -> str|None:
        """
        Returns the user identifier of a session if it has not expired.

        Args:
            session_token (str): The session token.

        Returns:
            str|None: The UUID of the user if the session is valid and not expired, None otherwise.
        """
        async with aiosqlite.connect(self.db_path) as db:
            query = '''
                SELECT uuid, expiry
                FROM Sessions
                WHERE session_token = ?
            '''
            async with db.execute(query, (session_token,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    user_uuid, expiry = row
                    if expiry > time.time():
                        return uuid.UUID(user_uuid)
                await self.delete(session_token)
                return None

    async def cocurrent_sessions(self, user_uuid) -> list[tuple[str, str]]:
        """
        Returns all sessions of a user.

        Args:
            user_uuid: The UUID of the user.

        Returns:
            list[tuple[str, str]]: A list of tuples containing session token and creation IP.
        """
        if isinstance(user_uuid, uuid.UUID):
            user_uuid = user_uuid.hex
        async with aiosqlite.connect(self.db_path) as db:
            query = '''
                SELECT session_token, creation_ip, expiry, created_at
                FROM Sessions
                WHERE uuid = ?
            '''
            async with db.execute(query, (user_uuid,)) as cursor:
                return await cursor.fetchall() ## hexed uuids

    async def delete(self, session_token: str) -> None:
        """
        Deletes a session.

        Args:
            session_token (str): The session token.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions WHERE session_token = ?', (session_token,))
            await db.commit()

    async def clear(self) -> None:
        """
        Clears all sessions from the database.

        Returns:
            None
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions')
            await db.commit()
