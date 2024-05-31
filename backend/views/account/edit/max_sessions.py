import re
from core.general import inject_cached_user, restricted_to_verified
from core.responses import success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db

URL_REGEX = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")

class UpdateMaxSessions(HTTPMethodView):
    """The update avatar view."""

    class UpdateMaxSessionsRequest(BaseModel):
        """The update avatar request model."""

        max_sessions: int

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    @parse_params(body=UpdateMaxSessionsRequest)
    async def post(request: Request, user, params: UpdateMaxSessionsRequest):
        """The update max sessions route."""
        cache = request.app.ctx.cache

        if params.max_sessions > 10:
            raise BadRequest("The max session limit cannot be higher than 10.")
        
        if params.max_sessions <= 0:
            raise BadRequest("The max session limit cannot be lower than 0.")

        if params.max_sessions < len(await request.app.ctx.session.cocurrent_sessions(user.uuid)):
            raise BadRequest("The max session limit cannot be lower than the current amount of active sessions.")
        
        if params.max_sessions == user.max_sessions:
            raise BadRequest("The max session limit cannot be the same as the current limit.")

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                await users_dal.update_user(user.uuid, max_sessions=params.max_sessions)

                await cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )

        return await success(request, "Maximum sessions updated successfully.")