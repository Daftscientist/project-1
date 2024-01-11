from core.responses import Success
from database.dals.user_dal import UsersDAL
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
from database import db
from core.encoder import hash_password, check_password


class UpdatePasswordView(HTTPMethodView):
    """The update password view."""

    class UpdatePasswordRequest(BaseModel):
        """The update password request model."""

        current_password: str
        new_password: str
        repeated_new_password: str

    @staticmethod
    @protected
    @parse_params(body=UpdatePasswordRequest)
    async def post(request: Request, params: UpdatePasswordRequest):
        """The update password route."""
        user = await request.app.ctx.cache.get(request)

        if len(params.new_password) < 8:
            raise BadRequest("Password must be at least 8 characters long.")
        if params.new_password != params.repeated_new_password:
            raise BadRequest("new passwords do not match.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                db_user = await users_dal.get_user_by_uuid(user.uuid)

                if not await check_password(params.current_password.encode('utf-8'), db_user.password):
                    raise BadRequest("Current password is incorrect.")

                await users_dal.update_user(
                    user.uuid, password=await hash_password(params.new_password.encode('utf-8'))
                )

        return await Success(request, "Password updated successfully.")