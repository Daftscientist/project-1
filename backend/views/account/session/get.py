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
        user = request.app.ctx.cache.get_user(request)
        ## save sessions in order of created [oldest first] (with id)
        sessions = request.app.ctx.session.cocurrent_sessions(user["uuid"])
        sessions = [fix_dict(session) for session in sessions]

        return await DataResponse(request, sessions)
