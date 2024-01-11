import re
from core.responses import DataResponse
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from core.general import fix_dict

class GetActiveSessionsView(HTTPMethodView):
    """The get active sessions view."""

    @staticmethod
    @protected
    async def post(request: Request):
        """The get active sessions route."""
        user = await request.app.ctx.cache.get(request)
        
        sessions = request.app.ctx.session.cocurrent_sessions(user.uuid)

        return await DataResponse(request, sessions)
