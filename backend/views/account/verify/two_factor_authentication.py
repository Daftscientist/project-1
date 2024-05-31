from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from sqlalchemy import update
from database.models.user import User
from database.dals.mfa_backup_codes_dal import Mfa_backup_codes_DAL
from core.responses import data_response, success
from database.dals.user_dal import UsersDAL
from core.authentication import protected
from core.general import restricted_to_verified, inject_cached_user
from database import db
from sanic_dantic import parse_params
from sanic_dantic import BaseModel
from core.general import generate_backup_code
from core import encoder

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
    async def post(request: Request, user, params: TwoFaSetupVerificationRequest):
        """ The 2fa setup otp verification route. """
        if not request.app.ctx.config["2fa"]["enabled"]:
            raise BadRequest("Two-factor authentication is not enabled on this server.")
        if not user.setting_up_two_factor_authentication:
            raise BadRequest("You are not currently in the proccess of setting up two-factor authentication.")
        if len(params.two_factor_authentication_otp_code) is not request.app.ctx.config["2fa"]["digits"]:
            raise BadRequest("Invalid OTP code.")
        
        async with db.async_session() as user_session:
            async with user_session.begin():
                users_dal = UsersDAL(user_session)
                db_user = await users_dal.get_user_by_uuid(user.uuid)

                if not db_user.verify_two_factor_auth(params.two_factor_authentication_otp_code):
                    raise BadRequest("Invalid OTP code.")
        
        data_to_return = []

        async with db.async_session() as backup_code_session:
            async with backup_code_session.begin():
                mfa_backup_codes_dal = Mfa_backup_codes_DAL(backup_code_session)
                await mfa_backup_codes_dal.delete_users_codes(user.uuid)

                for _ in range(request.app.ctx.config["2fa"]["backup_codes"]):
                    code = generate_backup_code(request.app.ctx.config["2fa"]["backup_code_length"])
                    data_to_return.append(code)
                    await mfa_backup_codes_dal.create_backup_code(user.uuid, code)
        
        async with db.async_session() as new_user_session:
            async with new_user_session.begin():
                new_users_dal = UsersDAL(new_user_session)
                
                ## update the item in db manually
                user.setting_up_two_factor_authentication = False
                user.two_factor_authentication_enabled = True

                ## push the new obj to the db

                q = update(User).where(User.uuid == user.uuid)
                q = q.values(user.to_dict())
                await new_user_session.execute(q)
                await new_user_session.flush()
                
                await request.app.ctx.cache.update(
                    await new_users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )
        return await data_response(request, {"backup_codes": data_to_return})