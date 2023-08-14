import re
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class UpdateEmailView(HTTPMethodView):
    """The update email view."""

    class UpdateEmailRequest(BaseModel):
        """The update email request model."""

        email: str
        repeated_email: str

    @protected
    @parse_params(body=UpdateEmailRequest)
    async def post(self, request: Request):
        """The update email route."""
        user = await get_user(request)

        

        return await DataResponse(request, {"user": user})