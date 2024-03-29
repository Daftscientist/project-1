"""
This module provides functions for handling cookies.
"""

import jwt
from sanic import json, Sanic
from sanic.request import Request

SECRET_KEY = (
    "hi my name is leo lmaoo"
    ## For testing only. This should be stored in an environment variable.
)
ALGORITHM = "HS256"

def send_cookie(request: Request, message:str, data: dict):
    """
    Sends a cookie with the specified message and data in the response.
    
    Args:
        request (Request): The request object.
        message (str): The message to include in the response.
        data (dict): The data to encode in the cookie.
    
    Returns:
        response: The response object with the cookie set.
    """
    response = json({
        "success": True,
        "message": message,
        "code": 200,
        "request_id": str(request.id)
    }, status=200)
    response.add_cookie(
        request.app.config.COOKIE_SESSION_NAME,
        jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM),
        httponly=True,
        ## max age 4 weeks
        max_age=request.app.ctx.SESSION_EXPIRY_IN,
    )
    return response

async def set_cookie(response, data: dict):
    """
    Sets a cookie with the specified data in the response.
    
    Args:
        response: The response object.
        data (dict): The data to encode in the cookie.
    
    Returns:
        response: The response object with the cookie set.
    """
    app = Sanic.get_app()
    response.add_cookie(
        app.config.COOKIE_SESSION_NAME,
        str(jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)),
        #domain='',
        httponly=True,
    )

    return response

def get_session_id(request):
    """
    Retrieve the session ID from the request cookies.

    Args:
        request (Request): The request object.

    Returns:
        str: The session ID.

    Raises:
        jwt.exceptions.DecodeError: If the session ID cannot be decoded from the cookie.
    """
    decoded = jwt.decode(
        request.cookies.get(request.app.config.COOKIE_SESSION_NAME),
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    return decoded["session_id"]

async def get_cookie(request):
    """
    Decode and return the cookie value from the request.

    Args:
        request: The request object containing the cookies.

    Returns:
        The decoded cookie value.

    """
    app = Sanic.get_app()
    return jwt.decode(
        request.cookies.get(app.config.COOKIE_SESSION_NAME), SECRET_KEY, algorithms=[ALGORITHM]
    )


async def remove_cookie(response):
    """
    Remove the session cookie from the response.

    Args:
        response (sanic.response.HTTPResponse): The response object.

    Returns:
        sanic.response.HTTPResponse: The updated response object.
    """
    app = Sanic.get_app()
    response.delete_cookie(app.config.COOKIE_SESSION_NAME)
    return response


async def check_if_cookie_is_present(request):
    """
    Checks if the cookie is present in the request.

    Args:
        request: The request object.

    Returns:
        bool: True if the cookie is present, False otherwise.
    """
    app = Sanic.get_app()
    return app.config.COOKIE_SESSION_NAME in request.cookies
