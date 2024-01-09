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
        #working


    async def get_user(self, request: sanic.Request):
        app = Sanic.get_app()
        session_token = get_session_id(request)
        uuid = app.ctx.session.get(session_token)

        if uuid is None:
            return Unauthorized("Authentication required.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)

                user = await users_dal.get_user_by_uuid(uuid)

                if user is None:
                    return Unauthorized("Authentication required.")
                
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