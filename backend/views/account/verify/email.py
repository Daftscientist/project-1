from sanic.views import HTTPMethodView
from sanic import BadRequest, Request
from database.dals.user_dal import UsersDAL
from database import db
from core.authentication import protected

class VerifyEmailView(HTTPMethodView):
    """The get user view."""

    @staticmethod
    @protected
    async def get(request: Request, identifier: str):
        """The email verification route."""
        cache = request.app.ctx.cache

        user_info = await cache.get_user(request)

        if user_info.email_verified:
            raise BadRequest("Email already verified.", status_code=400)
        
        if not identifier:
            raise BadRequest("No email verification code present in the request.", status_code=400)
        
        if identifier != user_info.email_verification_code:
            raise BadRequest("Invalid email verification code.", status_code=400)
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                await users_dal.update_user(uuid=user_info.uuid, email_verified=True)
                user_info.email_verified = True
                await cache.update(user_info)
