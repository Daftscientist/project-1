import json
import re
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected
from uuid import UUID
from datetime import date, datetime


EMAIL_REGEX = re.compile(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$")

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.__str__()
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        
        return json.JSONEncoder.default(self, obj)

class GetUserView(HTTPMethodView):
    """The get user view."""

    @staticmethod
    @protected
    async def post(request: Request):
        """The get user route."""
        user = await get_user(request)

        for item in user:
            print(item)
            print(user[item])
        

        user = json.dumps(user, cls=UUIDEncoder)
        #user = json.dumps(user, sort_keys=True, default=str)
        user = json.loads(user)
        return await DataResponse(request, user)