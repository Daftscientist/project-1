from sanic import Request
from core.responses import Success
from sanic.views import HTTPMethodView

class IndexView(HTTPMethodView):
    """The index view."""

    async def get(self, request: Request):
        return await Success(request, 'I am async get method')

    async def post(self, request: Request):
        return await Success(request, 'I am async post method')

    async def put(self, request: Request):
        return await Success(request, 'I am async put method')