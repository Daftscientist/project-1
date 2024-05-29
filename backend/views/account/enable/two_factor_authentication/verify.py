from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.responses import data_response, success
from database.dals.user_dal import UsersDAL
from core.authentication import protected
from core.general import restricted_to_verified, inject_cached_user
from database import db
from sanic_dantic import parse_params
from sanic_dantic import BaseModel

class TwoFaSetupVerificationView(HTTPMethodView):
    """The 2fa otp verification for setup view."""

    class TwoFaSetupVerificationRequest(BaseModel):
        """The 2fa setup verification request model."""

        two_factor_authentication_otp_code: str

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    @parse_params(body=TwoFaSetupVerificationRequest)
    async def get(request: Request, user, params: TwoFaSetupVerificationRequest):
        """ The 2fa setup otp verification route. """
        if not request.app.ctx.config["core"]["two_factor_authentication"]:
            raise BadRequest("Two-factor authentication is not enabled on this server.")
        if not user.setting_up_two_factor_authentication:
            raise BadRequest("You are not currently in the proccess of setting up two-factor authentication.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                db_user = await users_dal.get_user_by_uuid(user.uuid)

                if len(params.two_factor_authentication_otp_code) is not request.app.ctx.config["2fa"]["digits"]:
                    raise BadRequest("Invalid OTP code.")
                if not db_user.verify_two_factor_auth(params.two_factor_authentication_otp_code):
                    raise BadRequest("Invalid OTP code.")
                
                users_dal.update_user(user.uuid, setting_up_two_factor_authentication=False, two_factor_authentication_enabled=True)
                request.app.ctx.cache.update(await users_dal.get_user_by_uuid(user.uuid))

                return success(request, "Two-factor authentication has been successfully set up. The code from your client was valid.")