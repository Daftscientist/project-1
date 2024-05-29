import re
from core.responses import data_response
from sanic.views import HTTPMethodView
from sanic import Request, BadRequest
from core.authentication import protected
from core.general import fix_dict
from core.general import inject_cached_user

class GetActiveSessionsView(HTTPMethodView):
    """The get active sessions view."""

    @staticmethod
    @protected
    @inject_cached_user()
    async def post(request: Request, user):
        """The get active sessions route."""
        
        sessions = await request.app.ctx.session.cocurrent_sessions(user.uuid)

        result = []

        for item in sessions:
            result.append({
                "session_token": item[0],
                "creation_ip": item[1],
                "expiry": item[2],
                "created_at": item[3]
            })

        return await data_response(request, result)
