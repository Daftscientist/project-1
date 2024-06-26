from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.responses import data_response
from core.oauth.discord import DiscordOAuth
from core.cookies import check_oauth_cookie_present, send_oauth_cookie
from core.authentication import protected
from core.general import restricted_to_verified
from sanic_dantic import parse_params, BaseModel


class DiscordOauthLinkingView(HTTPMethodView):
    """The discord oauth view."""

    class DiscordOauthLinkingRequest(BaseModel):
        """The delete sessions request model."""

        rejoin_uri: str

    @staticmethod
    @protected
    @restricted_to_verified()
    @parse_params(body=DiscordOauthLinkingRequest)
    async def post(request: Request, params: DiscordOauthLinkingRequest):
        """ The discord oauth account linking route. """

        if not request.app.ctx.config["oauth"]["discord"]["enabled"]:
            raise BadRequest("Discord OAuth is not enabled on this server.")
        
        if check_oauth_cookie_present(request=request, identifier="discord_oauth"):
            raise BadRequest("You are already linking a discord account.")
        
        client = DiscordOAuth(
            redirect_uri=request.app.ctx.config["oauth"]["discord"]["link_redirect_uri"],
            scopes=request.app.ctx.config["oauth"]["discord"]["scopes"],
            client_id=request.app.ctx.config["oauth"]["discord"]["client_id"],
            client_secret=request.app.ctx.config["oauth"]["discord"]["client_secret"]
        )

        login_info = client.get_login_url()
        redirect_uri = login_info[0]

        response = await data_response(request, {"redirect_uri": redirect_uri})
        response = send_oauth_cookie(
            request=request,
            response=response, 
            identifier="discord_oauth",
            data={
                "state": login_info[1],
                "rejoin_uri": params.rejoin_uri
            }
        )
        return response