from core.responses import Success
from sanic import Request, Unauthorized, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import remove_cookie, get_session_id
from core.authentication import protected

class LogoutView(HTTPMethodView):
    """The logout view."""

    @staticmethod
    @protected
    async def post(request: Request):
        """ The logout route. """
        app = request.app

        response = await Success(request, "Logged out successfully.")
        await remove_cookie(response)
        app.ctx.session.remove(get_session_id(request))
        ## delete the session info from cache
        return response