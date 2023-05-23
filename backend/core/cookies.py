import jwt

SECRET_KEY = '23893784023409283964732894790792848932798479012043789247589357838401293890' ## For testing only. This should be stored in an environment variable.
ALGORITHM = 'HS256'
COOKIE_IDENTITY = 'session'

async def set_cookie(response, data: dict):
    """Sets the cookie in the response."""
    response.add_cookie(
        COOKIE_IDENTITY,
        jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM),
        httponly=True,
    )
    return response

async def get_cookie(request):
    """Gets the cookie from the request."""
    return jwt.decode(request.cookies.get(COOKIE_IDENTITY), SECRET_KEY, algorithms=[ALGORITHM])

async def remove_cookie(response):
    """Removes the cookie from the response."""
    response.del_cookie(COOKIE_IDENTITY)
    return response

async def check_if_cookie_is_present(request):
    """Checks if the cookie is present."""
    return COOKIE_IDENTITY in request.cookies