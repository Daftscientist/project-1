from sanic import json, Request

async def hello_route(request: Request):
    return json({'hi': 'hello'})