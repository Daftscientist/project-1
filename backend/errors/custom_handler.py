"""
This module provides a custom error handler for the backend application.
"""

import datetime
import sanic
from sanic.handlers import ErrorHandler


class CustomErrorHandler(ErrorHandler):
    """
    Custom error handler class that handles errors that have no error handlers assigned.
    """

    def default(self, request: sanic.Request, exception: Exception) -> sanic.HTTPResponse:
        """
        Default error handler for the custom error handler class.
        
        Args:
            request (sanic.Request): The request object.
            exception (Exception): The exception object.
        
        Returns:
            sanic.HTTPResponse: The HTTP response containing the error details.
        """
        status_code = getattr(exception, "status_code", 500)
        return sanic.json({
            "error": str(exception),
            "status": status_code,
            "path": request.path,
            "request_id": str(request.id),
            "timestamp": str(datetime.datetime.now())
        }, status=status_code)
