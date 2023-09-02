import re
from core.responses import Success
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected
from core.session import get_users_sessions
from sanic_dantic import parse_params, BaseModel
from core.session import session_data, delete_user
from core.cookies import get_cookie

class DeleteSessionView(HTTPMethodView):
    """The delete sessions view."""

    class DeleteSessionRequest(BaseModel):
        """The delete sessions request model."""

        session_id: str

    @staticmethod
    @protected
    @parse_params(body=DeleteSessionRequest)
    async def post(request: Request, params: DeleteSessionRequest):
        """The delete sessions route."""
        ##fix this
        print(params.session_id)
        print(session_data)
        print("hi", -params.session_id in list(session_data.keys()))
        if not str(params.session_id) in list(session_data.keys()):
            raise BadRequest("Session does not exist.")
        
        res = delete_user(params.session_id)
        print(res)
        if res == False:
            raise BadRequest("Session does not exist.")

        return await Success(request, "Session deleted successfully.")