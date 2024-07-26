import time
import datetime
import secrets
from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.oauth.google import GoogleOAuth
from database.dals.user_dal import UsersDAL
from database import db
from core.cookies import check_if_cookie_is_present, check_oauth_cookie_present, del_oauth_cookie, get_oauth_cookie, send_cookie
from core.authentication import protected

def create_session_id():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16)

class GoogleOauthCallbackView(HTTPMethodView):
    """The Google OAuth callback view."""

    @staticmethod
    async def get(request: Request):
        """ The Google OAuth callback route. """

        last_login = datetime.datetime.now()

        if not request.app.ctx.config["oauth"]["google"]["enabled"]:
            raise BadRequest("Google OAuth is not enabled on this server.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        client = GoogleOAuth(
            redirect_uri=request.app.ctx.config["oauth"]["google"]["login_redirect_uri"],
            scopes=request.app.ctx.config["oauth"]["google"]["scopes"],
            client_id=request.app.ctx.config["oauth"]["google"]["client_id"],
            client_secret=request.app.ctx.config["oauth"]["google"]["client_secret"]
        )

        if not check_oauth_cookie_present(request=request, identifier="google_oauth"):
            raise BadRequest("You have not started linking a Google account.")

        fetched_data = client.fetch_token(request)

        token = fetched_data[0]
        state = fetched_data[1]

        if token is None or state is None:
            raise BadRequest("Failed to fetch Google account information.")

        if state != get_oauth_cookie(request, "google_oauth")["state"]:
            raise BadRequest("Invalid state parameter received from Google.")

        details = client.oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
        try:
            google_user_info = details.json()
        except Exception:
            raise BadRequest("Failed to fetch Google account information.")

        email = google_user_info.get("email")
        google_id = google_user_info.get("id")
        picture = google_user_info.get("picture")
        verified_email = google_user_info.get("verified_email")

        if email is None or google_id is None:
            raise BadRequest("Failed to fetch Google account information.")

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)

                user_info = await users_dal.get_user_by_google_id(google_id)

                if user_info is None:
                    raise BadRequest("Account does not exist.")

                if google_id != user_info.google_account_identifier:
                    raise BadRequest("Account does not exist.")

                if user_info.max_sessions <= len(await request.app.ctx.session.concurrent_sessions(user_info.uuid)):
                    raise BadRequest("You have too many concurrent sessions.")

                uuid = user_info.uuid

                session_id = create_session_id()

                user_ip = request.remote_addr or request.ip

                await request.app.ctx.session.add(session_id, uuid, user_ip, time.time() + request.app.ctx.SESSION_EXPIRY_IN)
                if not len(await request.app.ctx.session.concurrent_sessions(user_info.uuid)) > 1:
                    await request.app.ctx.cache.update(user_info)

                await users_dal.update_user(uuid=uuid, last_login=last_login, latest_ip=user_ip)

                await request.app.ctx.cache.update(
                    await users_dal.get_user_by_uuid(uuid)
                )

                if user_info.two_factor_authentication_enabled and not verified_email and request.app.ctx.config["2fa"]["enabled"]:
                    await request.app.ctx.session.change_twofactor_auth_state(session_id, True)
                    response = send_cookie(request, "Logged in successfully. Your access is limited until you confirm your 2fa code.", {"session_id": session_id})
                else:
                    response = send_cookie(request, "Logged in successfully.", {"session_id": session_id})

                # Delete the cookie
                response = del_oauth_cookie(response, "google_oauth")

                return response
