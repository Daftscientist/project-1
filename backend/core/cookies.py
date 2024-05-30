"""
This module provides functions for handling cookies.
"""

import jwt
from sanic import json, Sanic
from sanic.request import Request

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
        request.app.ctx.config['session']['cookie_identifier'],
        jwt.encode(data, 
            request.app.ctx.config["core"]["cookie_secret"],
            algorithm=request.app.ctx.config["core"]["cookie_algorithm"]
        ),
        httponly=request.app.ctx.config['session']['cookie_secure'],
        ## max age 4 weeks
        max_age=request.app.ctx.config['session']['session_max_age'],
        path="/"
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
        request.cookies.get(request.app.ctx.config['session']['cookie_identifier']),
        request.app.ctx.config["core"]["cookie_secret"],
        algorithms=[request.app.ctx.config["core"]["cookie_algorithm"]]
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
        request.cookies.get(
            app.ctx.config['session']['cookie_identifier']),
            request.app.ctx.config["core"]["cookie_secret"],
            algorithms=[request.app.ctx.config["core"]["cookie_algorithm"]]
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
    response.delete_cookie(app.ctx.config['session']['cookie_identifier'])
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
    return app.ctx.config['session']['cookie_identifier'] in request.cookies
