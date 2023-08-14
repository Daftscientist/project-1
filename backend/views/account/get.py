import json
import re
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected
from uuid import UUID
from datetime import date, datetime
from core.general import fix_dict


EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")



class GetUserView(HTTPMethodView):
    """The get user view."""

    @staticmethod
    @protected
    async def post(request: Request):
        """The get user route."""
        user = await get_user(request)

        user = fix_dict(user)
        
        return await DataResponse(request, user)