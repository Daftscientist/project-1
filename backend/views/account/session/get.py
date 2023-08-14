import re
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.cookies import get_user
from core.authentication import protected
from core.session import get_users_sessions

class GetActiveSessionsView(HTTPMethodView):
    """The get active sessions view."""

    @staticmethod
    @protected
    async def post(request: Request):
        """The get active sessions route."""
        user = await get_user(request)

        sessions = await get_users_sessions(user["uuid"])

        print(sessions)

        return await DataResponse(request, {"sessions": sessions})