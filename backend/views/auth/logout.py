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
        cache = request.app.ctx.cache
        session = app.ctx.session

        user = await cache.get(request)

        if len(await session.cocurrent_sessions(user.uuid)) <= 1:
            # last session
            await cache.remove(user.uuid)

        response = await Success(request, "Logged out successfully.")
        response = await remove_cookie(response)

        await app.ctx.session.delete(get_session_id(request))
        ## delete the session info from cache
        return response