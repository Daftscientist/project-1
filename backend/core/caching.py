import pickle
import sqlite3
from sanic import Sanic
from sanic import Unauthorized
import sanic
from database.dals.user_dal import UsersDAL
from database import db
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

    async def add(self,user_info) -> None:
        """Adds a session to the cache."""

        uuid = user_info.uuid

        if uuid is None:
            return Unauthorized("Authentication required.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)

                user = user_info

                if user is None:
                    return Unauthorized("Authentication required.")
                
                
                self.cursor.execute('INSERT OR REPLACE INTO Sessions (user_identifier, data) VALUES (?, ?)', 
                                    (user.uuid.hex, pickle.dumps(user, pickle.HIGHEST_PROTOCOL,)))
                self.conn.commit()

    async def get(self, request: sanic.Request):
        app = Sanic.get_app()
        uuid = app.ctx.session.get(get_session_id(request))

        if uuid is None:
            return Unauthorized("Authentication required.")
        
        self.cursor.execute('SELECT data FROM Sessions WHERE user_identifier = ?', (uuid.hex,))
        row = self.cursor.fetchone()
        if row is not None:
            return pickle.loads(row[0])
                

    async def get_user(self, request: sanic.Request):
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