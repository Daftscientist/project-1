import json
import re
from core.responses import data_response
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from uuid import UUID
from datetime import date, datetime
from core.general import fix_dict, inject_cached_user, restricted_to_verified

EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")



class GetUserView(HTTPMethodView):
    """The get user view."""

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    async def post(request: Request, user):
        """The get user route."""
        user_data = fix_dict(user.to_dict())
        return await data_response(request, user_data)