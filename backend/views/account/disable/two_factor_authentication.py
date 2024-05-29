import re
from core.responses import success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db
from core.general import inject_cached_user, restricted_to_verified

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class DisableTwoFaView(HTTPMethodView):
    """The update email view."""

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    async def post(request: Request, user):
        """The disable two factor authentication route."""

        cache = request.app.ctx.cache

        if not user.two_factor_authentication_enabled:
            raise BadRequest("Two-factor authentication is not enabled on this account.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                await users_dal.update_user(user.uuid, two_factor_authentication_enabled=False, setting_up_two_factor_authentication=False)

                await cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )

        return await success(request, "Successfully disabled two-factor authentication.")