import re
from core.responses import Success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db

URL_REGEX = re.compile(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")

class UpdateAvatarView(HTTPMethodView):
    """The update avatar view."""

    class UpdateAvatarRequest(BaseModel):
        """The update avatar request model."""

        new_avatar: str

    @staticmethod
    @protected
    @parse_params(body=UpdateAvatarRequest)
    async def post(request: Request, params: UpdateAvatarRequest):
        """The update avatar route."""
        user = await request.app.ctx.cache.get_user(request)

        if not URL_REGEX.fullmatch(params.new_avatar):
            raise BadRequest("Avatar must be a valid URL.")
        if not params.new_avatar.endswith((".png", ".jpg", ".jpeg", ".gif")):
            raise BadRequest("Avatar must be a valid image URL.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                await users_dal.update_user(user["uuid"], avatar=params.new_avatar)

                #edit_user(user["session_id"], avatar=params.new_avatar)

        return await Success(request, "Avatar updated successfully.")