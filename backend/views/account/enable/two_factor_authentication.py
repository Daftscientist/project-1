from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from database.dals.mfa_backup_codes_dal import Mfa_backup_codes_DAL
from core.responses import data_response
from database.dals.user_dal import UsersDAL
from core.cookies import check_if_cookie_is_present
from core.authentication import protected
from core.general import restricted_to_verified, inject_cached_user
from io import BytesIO
import qrcode
from base64 import b64encode
from database import db
from core.general import generate_backup_code

def get_b64encoded_qr_image(data):
    print(data)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered)
    return b64encode(buffered.getvalue()).decode("utf-8")

class TwoFaSetupView(HTTPMethodView):
    """The 2fa setup view view."""

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    async def post(request: Request, user):
        """ The 2fa setup route. """
        if not request.app.ctx.config["2fa"]["enabled"]:
            raise BadRequest("Two-factor authentication is not enabled on this server.")
        if user.setting_up_two_factor_authentication:
            raise BadRequest("Two-factor authentication is already in the process of being set up on this account.")
        
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                db_user = await users_dal.get_user_by_uuid(user.uuid)
                setup_uri = db_user.get_two_factor_auth_setup_uri()

                ## generate qr code
                qr_image = get_b64encoded_qr_image(setup_uri) # use in href as src="data:image/png;base64,{{ qr_image }}"
                
                data_to_return = {"qr_image": qr_image, "setup_uri": setup_uri, "secret_token": db_user.two_factor_authentication_secret}

                await users_dal.update_user(user.uuid, setting_up_two_factor_authentication=True)
                await request.app.ctx.cache.update(await users_dal.get_user_by_uuid(user.uuid))

                return await data_response(request, data_to_return)