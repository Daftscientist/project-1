import aiosqlite
import time
import uuid

class SessionManager:
    """A session manager that stores sessions in a SQLite database."""
    def __init__(self, db_path: str):
        """Initializes the session manager."""
        self.db_path = db_path
    
    async def async__init__(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS Sessions (
                    session_token TEXT PRIMARY KEY,
                    uuid TEXT,
                    creation_ip TEXT,                
                    expiry INTEGER,
                    created_at INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')
            await db.commit()
            await self.session_cleanup()

    async def get_all_users(self) -> list[str]:
        """Returns all users in the cache."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT uuid FROM Sessions') as cursor:
                return list(set([row for row in await cursor.fetchall()]))

    async def session_cleanup(self) -> None: ## decide whether this runs per action or periodically.
        """Removes all expired sessions from the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions WHERE expiry <= ?', (time.time(),))
            await db.commit()

    async def add(self, session_token: str, user_uuid: str, creation_ip: str, expiry: int) -> None:
        """Adds a session to the cache."""
        if expiry <= time.time():
            raise ValueError("Expiry must be a future Unix timestamp.")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR REPLACE INTO Sessions (session_token, uuid, creation_ip, expiry) VALUES (?, ?, ?, ?)', 
                                (session_token, user_uuid.hex, creation_ip, expiry))
            await db.commit()

    async def check_session_token(self, session_token: str) -> bool:
        """Returns whether a session token is valid."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT expiry FROM Sessions WHERE session_token = ? ORDER BY created_at ASC', (session_token,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    expiry = row[0]
                    if expiry > time.time():
                        return True
                await self.delete(session_token)
                return False

    async def get(self, session_token: str) -> str|None:
        """Returns the user identifier of a session if it has not expired."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT uuid, expiry FROM Sessions WHERE session_token = ?', (session_token,)) as cursor:
                row = await cursor.fetchone()
                if row is not None:
                    user_uuid, expiry = row
                    if expiry > time.time():
                        return uuid.UUID(user_uuid)
                await self.delete(session_token)
                return None

    async def cocurrent_sessions(self, user_uuid) -> list[tuple[str, str]]:
        """Returns all sessions of a user."""
        if type(user_uuid) == uuid.UUID:
            user_uuid = user_uuid.hex
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT session_token, creation_ip, expiry, created_at FROM Sessions WHERE uuid = ?', (user_uuid,)) as cursor:
                return await cursor.fetchall() ## hexed uuids

    async def delete(self, session_token: str) -> None:
        """Deletes a session."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions WHERE session_token = ?', (session_token,))
            await db.commit()

    async def clear(self) -> None:
        """Clears all sessions."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM Sessions')
            await db.commit()
