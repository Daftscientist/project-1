import re
from core.responses import Success
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
    @parse_params(body=UpdateMaxSessionsRequest)
    async def post(request: Request, params: UpdateMaxSessionsRequest):
        """The update avatar route."""
        user = await request.app.ctx.cache.get(request)
        cache = request.app.ctx.cache

        if params.max_sessions > 10:
            raise BadRequest("The max session limit cannot be higher than 10.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                await users_dal.update_user(user.uuid, max_sessions=params.max_sessions)

                await cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )

        return await Success(request, "Maximum sessions updated successfully.")