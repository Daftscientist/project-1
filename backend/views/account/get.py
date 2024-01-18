import json
import re
from core.responses import data_response
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
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
        cache = request.app.ctx.cache

        user = fix_dict(await cache.get_user(request))
        
        return await data_response(request, user)