import sqlite3
import time

class SessionManager:
    """A session manager that stores sessions in a SQLite database."""
    def __init__(self, db_path: str):
        """Initializes the session manager."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sessions (
                session_token TEXT PRIMARY KEY,
                user_identifier TEXT,
                creation_ip TEXT,                
                expiry INTEGER,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        self.conn.commit()

    def session_cleanup(self) -> None: ## decide whether this runs per action or periodically.
        """Removes all expired sessions from the database."""
        self.cursor.execute('DELETE FROM Sessions WHERE expiry <= ?', (time.time(),))
        self.conn.commit()

    def add(self, session_token: str, user_identifier: str, creation_ip: str, expiry: int) -> None:
        """Adds a session to the cache."""
        if expiry <= time.time():
            raise ValueError("Expiry must be a future Unix timestamp.")
        self.cursor.execute('INSERT OR REPLACE INTO Sessions (session_token, user_identifier, creation_ip, expiry) VALUES (?, ?, ?, ?)', 
                            (session_token, user_identifier, creation_ip, expiry))
        self.conn.commit()

    def get(self, session_token: str) -> str|None:
        """Returns the user identifier of a session if it has not expired."""
        self.cursor.execute('SELECT user_identifier, expiry FROM Sessions WHERE session_token = ?', (session_token,))
        row = self.cursor.fetchone()
        if row is not None:
            user_identifier, expiry = row
            if expiry > time.time():
                return user_identifier
        self.delete(session_token)
        return None

    def check_session_token(self, session_token: str) -> bool:
        """Returns whether a session token is valid."""
        self.cursor.execute('SELECT expiry FROM Sessions WHERE session_token = ?', (session_token,))
        row = self.cursor.fetchone()
        if row is not None:
            expiry = row[0]
            if expiry > time.time():
                return True
        self.delete(session_token)
        return False

    def cocurrent_sessions(self, user_identifier) -> list[tuple[str, str]]:
        """Returns all sessions of a user."""
        self.cursor.execute('SELECT session_token, creation_ip, expiry, created_at FROM Sessions WHERE user_identifier = ?', (user_identifier,))
        return self.cursor.fetchall()

    def delete(self, session_token: str) -> None:
        """Deletes a session."""
        self.cursor.execute('DELETE FROM Sessions WHERE session_token = ?', (session_token,))
        self.conn.commit()

    def clear(self) -> None:
        """Clears all sessions."""
        self.cursor.execute('DELETE FROM Sessions')
        self.conn.commit()
