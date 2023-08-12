from core.responses import Success
from sanic import Request, Unauthorized, BadRequest
from sanic.views import HTTPMethodView
from core.cookies import check_if_cookie_is_present, remove_cookie, get_cookie
from core.cache import get_uuid, get


class LogoutView(HTTPMethodView):
    """The logout view."""

    async def post(self, request: Request):
        """ The logout route. """

        ## check if cookies are present
        if not await check_if_cookie_is_present(request):
            return await Unauthorized("Authentication required.")
        
        ## check if session info is present in cache
        cookie = await get_cookie(request)
        uuid = cookie["uuid"]
        if uuid is None:
            raise Unauthorized("Authentication required.")
        if get(uuid) is None:
            raise Unauthorized("Authentication required.")
        if get(uuid)["session_id"] is None:
            raise Unauthorized("Authentication required.")
        if get(uuid)["session_id"] != cookie["session_id"]:
            raise Unauthorized("Authentication required.")

        response = Success(request, "Logged out successfully.")
        await remove_cookie(response)
        ## delete the session info from cache
        return response