"""
Module docstring goes here.
"""

import re
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from sanic_dantic import parse_params
from sanic_dantic import BaseModel
# pylint: disable=import-error
from core.authentication import protected
from core.responses import success
from database.dals.user_dal import UsersDAL
from database import db
from core.general import inject_cached_user

URL_REGEX = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}"
    r"\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)

class UpdateAvatarView(HTTPMethodView):
    """The update avatar view."""

    class UpdateAvatarRequest(BaseModel):
        """The update avatar request model."""

        new_avatar: str

    @staticmethod
    @protected
    @inject_cached_user()
    @parse_params(body=UpdateAvatarRequest)
    async def post(request: Request, user, params: UpdateAvatarRequest):
        """
        Update the avatar of the user.

        Args:
            request (Request): The request object.
            params (UpdateAvatarRequest): The request parameters.

        Raises:
            BadRequest: If the new avatar URL is invalid or not an image URL.

        Returns:
            Response: The response object indicating the success of the operation.
        """
        cache = request.app.ctx.cache

        if not URL_REGEX.fullmatch(params.new_avatar):
            raise BadRequest("Avatar must be a valid URL.")
        if not params.new_avatar.endswith((".png", ".jpg", ".jpeg", ".gif")):
            raise BadRequest("Avatar must be a valid image URL.")

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)

                await users_dal.update_user(user.uuid, avatar=params.new_avatar)

                await cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )

        return await success(request, "Avatar updated successfully.")
