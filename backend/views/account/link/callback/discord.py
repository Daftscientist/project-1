from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.responses import success
from core.oauth.discord import DiscordOAuth
from database.dals.user_dal import UsersDAL
from database import db
from core.cookies import check_oauth_cookie_present, get_oauth_cookie, del_oauth_cookie
from core.authentication import protected
from core.general import inject_cached_user, restricted_to_verified


class DiscordOauthLinkCallbackView(HTTPMethodView):
    """The discord oauth link callback view."""

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    async def get(request: Request, user):
        """ The discord oauth callback route. """

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")

        client = DiscordOAuth(
            redirect_uri=request.app.ctx.config["oauth"]["discord"]["link_redirect_uri"],
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
                
                if user.discord_account_identifier is not None:
                    raise BadRequest("Account is already linked to a discord account. Please unlink the account first.")
                
                if user.avatar is None:
                    await users_dal.update_user(uuid=user.uuid, avatar=avatar)

                if not user.email_verified:
                    if user.email == email:
                        await users_dal.update_user(uuid=user.uuid, email_verified=_verified)

                await users_dal.update_user(uuid=user.uuid, discord_account_identifier=_id)

                await request.app.ctx.cache.update(
                    await users_dal.get_user_by_uuid(
                        user.uuid
                    )
                )
                response = success("Successfully linked discord account.")
                ## delete the cookie
                response = del_oauth_cookie(response, "discord_oauth")

                return response