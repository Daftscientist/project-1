import jwt
from sanic import json
from core.session import get_user as fetch_user

SECRET_KEY = "23893784023409283964732894790792848932798479012043789247589357838401293890"  ## For testing only. This should be stored in an environment variable.
ALGORITHM = "HS256"
COOKIE_IDENTITY = "session"

def send_cookie(request, message:str, data: dict):
    """Sends the cookie in the response."""
    response = json({
        "success": True,
        "message": message,
        "code": 200,
        "request_id": str(request.id)
    }, status=200)
    response.add_cookie(
        COOKIE_IDENTITY,
        jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM),
        httponly=False,
        max_age=86400
    )
    return response

async def set_cookie(response, data: dict):
    """Sets the cookie in the response."""
    response.add_cookie(
        COOKIE_IDENTITY,
        str(jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)),
        httponly=True,
    )
    response.add_cookie(
        "test",
        "It worked!",
        domain=".yummy-yummy-cookie.com",
        httponly=True
    )
    return response

async def get_user(request):
    """Gets the user from the cookie."""
    decoded = jwt.decode(
        request.cookies.get(COOKIE_IDENTITY), SECRET_KEY, algorithms=[ALGORITHM])
    return fetch_user(decoded["session_id"])

async def get_cookie(request):
    """Gets the cookie from the request."""
    return jwt.decode(
        request.cookies.get(COOKIE_IDENTITY), SECRET_KEY, algorithms=[ALGORITHM]
    )


async def remove_cookie(response):
    """Removes the cookie from the response."""
    response.delete_cookie(COOKIE_IDENTITY)
    return response


async def check_if_cookie_is_present(request):
    """Checks if the cookie is present."""
    return COOKIE_IDENTITY in request.cookies
