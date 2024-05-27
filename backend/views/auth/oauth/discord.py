from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present
from core.authentication import protected

class DiscordOauthView(HTTPMethodView):
    """The discord oauth view."""

    @staticmethod
    @protected
    async def get(request: Request):
        """ The discord oauth route. """

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
        
        return redirect(request.app.ctx.discord.generate_oauth_url())