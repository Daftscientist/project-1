"""
This module provides a function for handling successful responses.
"""

import sanic

async def success(request, data=None, code=200):
    """
    Create a success response.

    Args:
        request: The request object.
        data: The data to be included in the response. Defaults to None.
        code: The HTTP status code. Defaults to 200.

    Returns:
        The success response object.
    """
    response = sanic.json({
        "success": True,
        "result": data,
        "code": code,
        "request_id": str(request.id)
    }, status=code)
    return response

async def data_response(request, data=None, code=200):
    """
    Generate a JSON response with the provided data and status code.

    Args:
        request: The request object.
        data: The data to be included in the response.
        code: The HTTP status code for the response.

    Returns:
        The JSON response object.
    """
    response = sanic.json({
        "success": True,
        "result": data,
        "code": code,
        "request_id": str(request.id)
    }, status=code)
    return response
