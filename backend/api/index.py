""" The index route. """

from sanic import text, Request

async def index_route(request: Request) -> text:
    """ The index route. Returns a simple text response. """
    return text(f"OK, this is the index route. {request.url}.")