from sanic import Request, text
from database.dals.user_dal import UsersDAL

async def create_user_route(request: Request):
    """ The create user route. """
    try:
        body = request.json
    except Exception as e:
        return text(f"Error: {e}")

    return text(f"OK, this is the create user route. {request.json}")