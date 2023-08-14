from core.responses import Success
from sanic import Request, Unauthorized, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, remove_cookie, get_cookie
from core.authentication import protected
from core.session import get_user

class LogoutView(HTTPMethodView):
    """The logout view."""

    @protected
    async def post(self, request: Request):
        """ The logout route. """
        response = await Success(request, "Logged out successfully.")
        await remove_cookie(response)
        ## delete the session info from cache
        return response