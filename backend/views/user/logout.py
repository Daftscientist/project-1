from core.responses import Success
from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, remove_cookie


class LogoutView(HTTPMethodView):
    """The logout view."""

    async def post(self, request: Request):
        """ The logout route. """

        ## check if cookies are present
        if not await check_if_cookie_is_present(request):
            return await BadRequest(request, "You are not logged in.")
        
        ## check if session info is present in cache

        response = Success(request, "Logged out successfully.")
        await remove_cookie(response)
        ## delete the session info from cache
        return response