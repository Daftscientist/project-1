from sanic import Request
from core.responses import success
from sanic.views import HTTPMethodView

class HelloView(HTTPMethodView):
    """The hello view."""

    async def get(self, request: Request):
        return await success(request, 'I am async get method')

    async def post(self, request: Request):
        return await success(request, 'I am async post method')

    async def put(self, request: Request):
        return await success(request, 'I am async put method')