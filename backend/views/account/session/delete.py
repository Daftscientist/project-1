import re
from core.responses import Success
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from sanic_dantic import parse_params, BaseModel
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
        #delete_user(params.session_id)
        return await Success(request, "Session deleted successfully.")
