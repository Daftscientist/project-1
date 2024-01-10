from sanic.exceptions import SanicException
import sanic
import datetime
from sanic.handlers import ErrorHandler


class CustomErrorHandler(ErrorHandler):


    def default(self, request: sanic.Request, exception: Exception) -> sanic.HTTPResponse:
        ''' handles errors that have no error handlers assigned '''

        status_code = getattr(exception, "status_code", 500)
        return sanic.json({
            "error": str(exception),
            "status": status_code,
            "path": request.path,
            "request_id": str(request.id),
            "timestamp": str(datetime.datetime.now())
        }, status=status_code)




        

