from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present
from core.authentication import protected

class DiscordOauth(HTTPMethodView):
    """The discord oauth view."""

    @staticmethod
    @protected
    async def post(request: Request):
        """ The discord oauth route. """

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        