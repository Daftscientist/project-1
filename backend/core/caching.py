import pickle
import sqlite3
from sanic import Sanic
from sanic import Unauthorized
import sanic
from database.models.user import User
from core.cookies import get_session_id

class Cache:
    """A caching manager that stores cache in a SQLite database."""
    def __init__(self, db_path: str):
        """Initializes the session manager."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sessions (
                user_identifier TEXT PRIMARY KEY,
                data BLOB,
                cached_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        self.conn.commit()

    async def add(self, user_info) -> None:
        """Adds a user to the cache."""
                
        self.cursor.execute('INSERT OR REPLACE INTO Sessions (user_identifier, data) VALUES (?, ?)', 
                                    (user_info.uuid.hex, pickle.dumps(user_info, pickle.HIGHEST_PROTOCOL,)))
        self.conn.commit()

    async def get(self, request: sanic.Request) -> User:
        """Gets a user from the cache."""
        app = Sanic.get_app()
        uuid = app.ctx.session.get(get_session_id(request))

        if uuid is None:
            return Unauthorized("Authentication required.")
        
        self.cursor.execute('SELECT data FROM Sessions WHERE user_identifier = ?', (uuid.hex,))
        row = self.cursor.fetchone()
        if row is not None:
            return pickle.loads(row[0])

    async def update(self, user_info: User) -> None:
        """Updates a user in the cache."""
        self.cursor.execute('INSERT OR REPLACE INTO Sessions (user_identifier, data) VALUES (?, ?)', 
                                    (user_info.uuid.hex, pickle.dumps(user_info, pickle.HIGHEST_PROTOCOL,)))
        self.conn.commit()

    async def remove(self, session_id: str) -> None:
        """Removes a user from the cache."""
        self.cursor.execute('DELETE FROM Sessions WHERE user_identifier = ?', (session_id,))
        self.conn.commit() 

    async def get_user(self, request: sanic.Request) -> dict:
        """Gets a user from the cache."""
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