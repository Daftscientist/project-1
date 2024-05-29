from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present
from core.authentication import protected
from core.general import restricted_to_verified


class DiscordOauthLinkingView(HTTPMethodView):
    """The discord oauth view."""

    @staticmethod
    @protected
    @restricted_to_verified()
    async def get(request: Request):
        """ The discord oauth account linking route. """

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")
        
        return redirect(request.app.ctx.discord.generate_oauth_url(redirect_uri=request.app.ctx.config["oauth"]["discord"]["link_redirect_uri"]))