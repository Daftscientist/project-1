from sanic import Request, text
from core.responses import Success

async def logout_route(request: Request):
    """ The logout route. """

    ## check if the user is logged in

    ## delete the cookie

    ## delete the session info from cache

    response = Success(request, "Logged out successfully.")
    return response