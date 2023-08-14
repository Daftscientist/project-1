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

class GetActiveSessionsView(HTTPMethodView):
    """The get active sessions view."""

    class DeleteSessionRequest(BaseModel):
        """The get active sessions request model."""

        session_id: str

    @staticmethod
    @protected
    @parse_params(body=DeleteSessionRequest)
    async def post(request: Request, params: DeleteSessionRequest):
        """The get active sessions route."""

        if not params.session_id in session_data:
            raise BadRequest("Session does not exist.")
        
        res = delete_user(params.session_id)

        if res == None:
            raise BadRequest("Session does not exist.")

        return await Success(request, "Session deleted successfully.")