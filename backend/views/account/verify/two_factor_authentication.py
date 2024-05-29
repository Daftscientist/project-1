from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from database.dals.mfa_backup_codes_dal import Mfa_backup_codes_DAL
from core.responses import data_response, success
from database.dals.user_dal import UsersDAL
from core.authentication import protected
from core.general import restricted_to_verified, inject_cached_user
from database import db
from sanic_dantic import parse_params
from sanic_dantic import BaseModel
from core.general import generate_backup_code

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

                data_to_return = {}

                if not db_user.two_factor_authentication_enabled:
                    mfa_backup_codes_dal = Mfa_backup_codes_DAL(session)
                    await mfa_backup_codes_dal.delete_users_codes(user.uuid)
                    for _ in range(request.app.ctx.config["2fa"]["backup_codes"]):
                        await mfa_backup_codes_dal.create_backup_code(user.uuid, generate_backup_code(request.app.ctx.config["2fa"]["backup_code_length"]))
                    data_to_return["backup_codes"] = [x.code for x in await mfa_backup_codes_dal.get_users_codes(user.uuid)]

                users_dal.update_user(user.uuid, setting_up_two_factor_authentication=False, two_factor_authentication_enabled=True)
                request.app.ctx.cache.update(await users_dal.get_user_by_uuid(user.uuid))

                return data_response(request, data_to_return)