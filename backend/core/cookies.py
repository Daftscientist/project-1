import jwt
from sanic import json
from core.session import get_user as fetch_user
from sanic.request import Request

SECRET_KEY = "23893784023409283964732894790792848932798479012043789247589357838401293890"  ## For testing only. This should be stored in an environment variable.
ALGORITHM = "HS256"
COOKIE_IDENTITY = "session"

def send_cookie(request: Request, message:str, data: dict):
    """ Sends a response containing a cookie with the data provided. """
    response = json({
        "success": True,
        "message": message,
        "code": 200,
        "request_id": str(request.id)
    }, status=200)
    response.add_cookie(
        COOKIE_IDENTITY,
        jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM),
        httponly=True,
        ## max age 4 weeks
        max_age=request.app.ctx.SESSION_EXPIRY_IN,
    )
    return response

async def set_cookie(response, data: dict):
    """ Attribiutes a cookie to a given response and returns the new response. """
    response.add_cookie(
        COOKIE_IDENTITY,
        str(jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)),
        #domain='',
        httponly=True,
    )
    
    return response

def get_session_id(request):
    """ Receives the user data from the cookie session id. """
    decoded = jwt.decode(
        request.cookies.get(COOKIE_IDENTITY), SECRET_KEY, algorithms=[ALGORITHM])
    return decoded["session_id"]

async def get_cookie(request):
    """ Fetches the cookie from the request. """
    return jwt.decode(
        request.cookies.get(COOKIE_IDENTITY), SECRET_KEY, algorithms=[ALGORITHM]
    )


async def remove_cookie(response):
    """ Removes the cookie from the response. """
    response.delete_cookie(COOKIE_IDENTITY)
    return response


async def check_if_cookie_is_present(request):
    """ Checks if the cookie is present in the request. """
    return COOKIE_IDENTITY in request.cookies
