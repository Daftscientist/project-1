""" The index route. """

from sanic import text

async def index_route(request) -> text:
    """ The index route. Returns a simple text response. """
    return text(f"OK, this is the index route. {request.url}.")