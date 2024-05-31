from database.dals.user_dal import UsersDAL
from database import db
from core.general import inject_cached_user
from core.responses import success
from sanic import Request, Unauthorized, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import remove_cookie, get_session_id
from core.authentication import protected_skip_2fa
from sanic_dantic import parse_params, BaseModel


class TwoFaVerifyLoginView(HTTPMethodView):
    """The verify two factor authentication view."""

    class TwoFaVerifyLoginRequest(BaseModel):
        """The create user request model."""

        otp_code: str

    @protected_skip_2fa
    @inject_cached_user()
    @parse_params(body=TwoFaVerifyLoginRequest)
    async def post(self, request: Request, user, params: TwoFaVerifyLoginRequest):
        """ The verify two factor authentication route. """
        app = request.app
        session = app.ctx.session

        if not request.app.ctx.config["2fa"]["enabled"]:
            raise BadRequest("Two-factor authentication is not enabled on this server.")

        if not session.get_twofactor_auth_state(get_session_id(request)):
            raise BadRequest("You are not required to verify two-factor authentication.")

        if not user.two_factor_authentication_enabled:
            raise BadRequest("Two-factor authentication is not enabled for this account.")
        
        if len(params.otp_code) is not request.app.ctx.config["2fa"]["digits"]:
            raise BadRequest("Invalid OTP code.")
        

        ## open db
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                user_info = await users_dal.get_user_by_uuid(user.uuid)
                if not user_info.verify_two_factor_auth(params.otp_code):
                    raise BadRequest("Invalid OTP code.")
                
                ## done with checking - now remove the 2fa state

                await session.change_twofactor_auth_state(get_session_id(request), False)

        return await success(request, "Two-factor authentication verified.")