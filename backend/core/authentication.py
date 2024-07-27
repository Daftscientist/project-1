
"""
This module provides functions for authentication and authorization in the application.
"""

import re
from sanic import BadRequest, Unauthorized, Request
import jwt
import sanic
import sanic.request

from core.cookies import get_session_id

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
    async def wrapper_func(request: sanic.Request, *args, **kwargs):

        is_authenticated = await check_authorization(request)
        if not is_authenticated:
            raise Unauthorized("Authentication required.")

        if request.app.ctx.config["2fa"]["enabled"] is True:
            session_id = get_session_id(request)
            if await request.app.ctx.session.get_twofactor_auth_state(session_id) is True:
                raise Unauthorized("Two-factor authentication verification required prior to accessing any protected routes.")

        response = await myfunc(request, *args, **kwargs)
        return response
    return wrapper_func

def protected_skip_2fa(myfunc):
    """
    Decorator function to protect routes by checking if authentication is present and skip 2FA.

    Args:
        myfunc: The function to be wrapped.

    Returns:
        The wrapped function.

    Raises:
        Unauthorized: If authentication is required.
    """
    async def wrapper_func(request: sanic.Request, *args, **kwargs):
        if not isinstance(request, sanic.Request):
            raise TypeError("Expected request to be an instance of sanic.Request")

        is_authenticated = await check_authorization(request)
        if not is_authenticated:
            raise Unauthorized("Authentication required.")

        response = await myfunc(request, *args, **kwargs)
        return response
    return wrapper_func

def root_admin_only(myfunc):
    """
    Decorator function to protect routes by checking if the user is a root admin.

    Args:
        myfunc: The function to be wrapped.

    Returns:
        The wrapped function.

    Raises:
        Unauthorized: If authentication is required.
    """
    async def wrapper_func(request: sanic.Request, *args, **kwargs):
        is_authenticated = await check_authorization(request)
        if not is_authenticated:
            raise Unauthorized("Authentication required.")
        user = await request.app.ctx.cache.get(request)
        if not user.is_root_admin:
            raise Unauthorized("Root admin only.")
        response = await myfunc(request, *args, **kwargs)
        return response
    return wrapper_func

## restrict to staff level
## this will be configurable 

def staff_only(myfunc):
    async def wrapper_func(request: sanic.Request, *args, **kwargs):
        is_authenticated = await check_authorization(request)
        if not is_authenticated:
            raise Unauthorized("Authentication required.")
        user = await request.app.ctx.cache.get(request)
        if not user.staff_level:
            raise Unauthorized("Staff only.")
        
        ## fetch the route endpoint and remove /api/{version}/ using regex from path
        context_path = request.app.ctx.config['routing']['context_path']
        enabled_versions = request.app.ctx.config['routing']['enabled_versions']

        request_info = None

        for version in enabled_versions:
            if version in request.path:
                request_version = version
                pattern = re.escape(f"{context_path}/{version}")
                request_path = re.sub(f"^{pattern}", "", request.path)
                request_path = f"/{request_path.lstrip('/')}"

                request_info = (request_version, request_path)
                break
        
        staff_level = user.staff_level

        #has_access = await staff_can_access(staff_level, request_version, request_path)
        
        #if not has_access:
        #    raise Unauthorized("Access denied.")

        # req_version, req_path = request_info


        # check if the user has access to the route
        ## database with staff level permissions creatable by a user. incremental numbers.
        ### these staff levels can have routes asigned to them i.e. with a version and path
        #### check the user's staff level in the user table
        ##### check if the users staff level has access to the spesified route by checking stafflevels table
        ###### if the user has access to the route, continue, else raise Unauthorized





        response = await myfunc(request, *args, **kwargs)
        return response
    return wrapper_func