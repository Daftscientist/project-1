from core.responses import Success
from sanic import Request, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, set_cookie


class LoginView(HTTPMethodView):
    """The login view."""

    async def post(self, request: Request):
        """ The login route. """

        ## check if cookies are present
        if await check_if_cookie_is_present(request):
            return await BadRequest(request, "You are already logged in.")
        
        ## check if session info is present in cache


        response = Success(request, "Logged in successfully.")
        await set_cookie(response, {"username": "test"})  ## set the session info in cache
        ## delete the session info from cache
        return response