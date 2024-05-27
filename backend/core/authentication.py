
"""
This module provides functions for authentication and authorization in the application.
"""

from sanic import Unauthorized, Request
import jwt

def check_for_cookie(request):
    """
    Check if the request contains a valid cookie session.

    Args:
        request: The request object.

    Returns:
        True if the request contains a valid cookie session, False otherwise.
    """
    if request.cookies is None:
        return False
    if not request.app.ctx.config['session']['cookie_identifier'] in request.cookies:
        return False
    return True

async def check_authorization(request: Request):
    """ 
    Checks if the cookie is present and session is valid. 

    Args:
        request: The request object.

    Raises:
        Unauthorized: If authentication is required.

    Returns:
        True if the cookie is present and session is valid.
    """
    if not check_for_cookie(request):
        raise Unauthorized("Authentication required.")
    cookie = jwt.decode(
        request.cookies.get(request.app.ctx.config['session']['cookie_identifier']),
        request.app.ctx.config["core"]["cookie_secret"],
        algorithms=[request.app.ctx.config["core"]["cookie_algorithm"]]
    )
    if cookie["session_id"] is None:
        raise Unauthorized("Authentication required.")
    if not await request.app.ctx.session.check_session_token(cookie["session_id"]):
        raise Unauthorized("Authentication required.")
    return True

def protected(myfunc):
    """
    Decorator function to protect routes by checking if authentication is present.

    Args:
        myfunc: The function to be wrapped.

    Returns:
        The wrapped function.

    Raises:
        Unauthorized: If authentication is required.
    """
    async def wrapper_func(request, *args, **kwargs):
        """ 
        Wrapper for routes to check if authentication is present. 

        Args:
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            Unauthorized: If authentication is required.

        Returns:
            The response from the wrapped function.
        """
        is_authenticated = await check_authorization(request)
        if not is_authenticated:
            raise Unauthorized("Authentication required.")

        response = await myfunc(request, *args, **kwargs)
        return response
    return wrapper_func
