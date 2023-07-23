from sanic.exceptions import SanicException
import sanic
import datetime
from sanic.handlers import ErrorHandler


class CustomErrorHandler(ErrorHandler):
    def default(
        self, request: sanic.Request, exception: Exception
    ) -> sanic.HTTPResponse:
        """handles errors that have no error handlers assigned"""

        try:
            status_code = exception.status_code
        except AttributeError:
            status_code = 500

        logf = open("./localstorage/exceptions.log", "a")
        logf.write(
            f"ID: {str(request.id)} - Message: '{str(exception)}' - Code: {str(status_code)} - Timestamp: {str(datetime.datetime.now())}\n"
        )
        logf.close()

        return sanic.json(
            {
                "error": str(exception),
                "status": status_code,
                "path": request.path,
                "request_id": str(request.id),
                "timestamp": str(datetime.datetime.now()),
            },
            status=status_code,
        )
