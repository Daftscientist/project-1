import time
import datetime
import secrets
from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.oauth.discord import DiscordOAuth
from database.dals.user_dal import UsersDAL
from database import db
from core.cookies import check_if_cookie_is_present, check_oauth_cookie_present, del_oauth_cookie, get_oauth_cookie, send_cookie
from core.authentication import protected

def create_session_id():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16) 

class DiscordOauthCallbackView(HTTPMethodView):
    """The discord oauth callback view."""

    @staticmethod
    async def get(request: Request):
        """ The discord oauth callback route. """

        last_login = datetime.datetime.now()

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
        
        client = DiscordOAuth(
            redirect_uri=request.app.ctx.config["oauth"]["discord"]["login_redirect_uri"],
            scopes=request.app.ctx.config["oauth"]["discord"]["scopes"],
            client_id=request.app.ctx.config["oauth"]["discord"]["client_id"],
            client_secret=request.app.ctx.config["oauth"]["discord"]["client_secret"]
        )

        if not check_oauth_cookie_present(request=request, identifier="discord_oauth"):
            raise BadRequest("You have not started linking a discord account.")

        fetched_data = client.fetch_token(request)

        token = fetched_data[0]
        state = fetched_data[1]

        if token is None or state is None:
            raise BadRequest("Failed to fetch discord account information.")
        
        if state != get_oauth_cookie(request, "discord_oauth")["state"]:
            raise BadRequest("Invalid state parameter received from Discord.")
        
        details = client.oauth.get(f'{client.BASE_URL}/users/@me')
        try:
            discord_user_info = details.json()
        except Exception:
            raise BadRequest("Failed to fetch discord account information.")
        print(discord_user_info)
        email = discord_user_info.get("email")
        _id = discord_user_info.get("id")
        _hash = discord_user_info.get("avatar")
        _verified = discord_user_info.get("verified")
        mfa_enabled = discord_user_info.get("mfa_enabled")


        if email is None or _id is None:
            raise BadRequest("Failed to fetch discord account information.")
        
        if _hash.startswith('a_'):
            avatar = client.CDN_URL + 'avatars/' + _id + '/' + _hash + '.gif?size=1024'
        else:
            avatar = client.CDN_URL + 'avatars/' + _id + '/' + _hash + '.png?size=1024'


        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                user_info = await users_dal.get_user_by_discord_id(discord_user_info["id"])

                if user_info is None:
                    raise BadRequest("Account does not exist.")

                if _id != user_info.discord_account_identifier:
                    raise BadRequest("Account does not exist.")

                if user_info.max_sessions <= len(await request.app.ctx.session.cocurrent_sessions(user_info.uuid)):
                    raise BadRequest("You have too many concurrent sessions.")

                uuid = user_info.uuid
                
                session_id = create_session_id()

                user_ip = request.remote_addr or request.ip

                await request.app.ctx.session.add(session_id, uuid, user_ip, time.time() + request.app.ctx.SESSION_EXPIRY_IN)
                if not len(await request.app.ctx.session.cocurrent_sessions(user_info.uuid)) > 1:
                    await request.app.ctx.cache.update(user_info)

                await users_dal.update_user(uuid=uuid, last_login=last_login, latest_ip=user_ip)

                await request.app.ctx.cache.update(
                    await users_dal.get_user_by_uuid(uuid)
                )

                if user_info.two_factor_authentication_enabled is True & mfa_enabled != True & request.app.ctx.config["2fa"]["enabled"] is True:
                    await request.app.ctx.session.change_twofactor_auth_state(session_id, True)
                    response = send_cookie(request, "Logged in successfully. Your access is limited until you confirm your 2fa code.", {"session_id": session_id})
                else:
                    response = send_cookie(request, "Logged in successfully.", {"session_id": session_id})

                ## delete the cookie
                response = del_oauth_cookie(response, "discord_oauth")

                return response