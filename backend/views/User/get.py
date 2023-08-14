import re
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class GetUserView(HTTPMethodView):
    """The get user view."""

    @protected
    async def post(self, request: Request):
        """The get user route."""
        user = await get_user(request)

        return await DataResponse(request, {"user": user})