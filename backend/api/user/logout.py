from sanic import Request, text, BadRequest
from core.cookies import check_if_cookie_is_present, remove_cookie
from core.responses import Success

async def logout_route(request: Request):
    """ The logout route. """

    ## check if cookies are present
    if not await check_if_cookie_is_present(request):
        return await BadRequest(request, "You are not logged in.")
    
    ## check if session info is present in cache

    response = Success(request, "Logged out successfully.")
    await remove_cookie(response)
    ## delete the session info from cache
    return response