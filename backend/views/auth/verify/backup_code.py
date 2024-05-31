from core.encoder import check_password
from core import encoder
from database.dals.mfa_backup_codes_dal import Mfa_backup_codes_DAL
from database import db
from core.general import generate_backup_code, inject_cached_user
from core.responses import success
from sanic import Request, Unauthorized, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import remove_cookie, get_session_id
from core.authentication import protected_skip_2fa
from sanic_dantic import parse_params, BaseModel


class BackupCodeVerificationView(HTTPMethodView):
    """The verify two factor authentication backup code view."""

    class BackupCodeVerificationRequest(BaseModel):
        """The create user request model."""

        backup_code: str

    @protected_skip_2fa
    @inject_cached_user()
    @parse_params(body=BackupCodeVerificationRequest)
    async def post(self, request: Request, user, params: BackupCodeVerificationRequest):
        """ The verify two factor authentication backup code route. """
        app = request.app
        session = app.ctx.session

        if not request.app.ctx.config["2fa"]["enabled"]:
            raise BadRequest("Two-factor authentication is not enabled on this server.")

        if not session.get_twofactor_auth_state(get_session_id(request)):
            raise BadRequest("You are not required to verify two-factor authentication.")

        if not user.two_factor_authentication_enabled:
            raise BadRequest("Two-factor authentication is not enabled for this account.")
        
        if len(params.backup_code) is not request.app.ctx.config["2fa"]["backup_code_length"]:
            raise BadRequest("Invalid backup code.")
        

        ## open db
        async with db.async_session() as session:
            async with session.begin():
                mfa_backup_codes_dal = Mfa_backup_codes_DAL(session)
                if not len(await mfa_backup_codes_dal.get_users_codes(user.uuid)) > 0:
                    raise BadRequest("No backup codes available.")
                
                # ----- Janky (will be fixed in the future) -----
                found = False
                for code in await mfa_backup_codes_dal.get_users_codes(user.uuid): ## Codes are hashed - can't be seen
                    if check_password(params.two_factor_authentication_backup_code.encode('utf-8'), code.code):
                        found = True
                if not found:
                    raise BadRequest("Invalid backup code.")
                # ------------------------------------------------

                await mfa_backup_codes_dal.delete_code(user.uuid, params.backup_code)
                await session.change_twofactor_auth_state(get_session_id(request), False)

                if len(await mfa_backup_codes_dal.get_users_codes(user.uuid)) == 0: ## if after the proccess the backup codes are now none
                    ## get new backup codes
                    data_to_return = []
                    for _ in range(request.app.ctx.config["2fa"]["backup_codes"]):
                        generated_code = generate_backup_code(request.app.ctx.config["2fa"]["backup_code_length"])
                        data_to_return.append(generated_code)
                        await mfa_backup_codes_dal.create_backup_code(user.uuid, await encoder.hash_password(generated_code.encode('utf-8')))
                    return success("Two-factor authentication verified. Your backup codes have been reset.", {"backup_codes": data_to_return})

        return success("Two-factor authentication verified.")