from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from database.dals.user_dal import UsersDAL
from database import db
from core.cookies import check_if_cookie_is_present, send_cookie
from core.authentication import protected

class DiscordOauthLinkCallbackView(HTTPMethodView):
    """The discord oauth link callback view."""

    @staticmethod
    @protected
    async def get(request: Request):
        """ The discord oauth callback route. """

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")

        token = request.app.ctx.discord.handle_callback(request, redirect_uri=request.app.ctx.config["oauth"]["discord"]["link_redirect_uri"])
        discord_user_info = request.app.ctx.discord.get_user_info(token, redirect_uri=request.app.ctx.config["oauth"]["discord"]["link_redirect_uri"])

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                
                user_info = await users_dal.get_user_by_discord_id(discord_user_info["id"])

                if user_info.discord_account_identifier is not None:
                    raise BadRequest("Account is already linked to a discord account. Please unlink the account first.")

                if discord_user_info["id"] == user_info.discord_account_identifier:
                    raise BadRequest("Account is already linked to this discord account.")

                uuid = user_info.uuid
                
                await users_dal.update_user(uuid=uuid, discord_account_identifier=discord_user_info["id"])