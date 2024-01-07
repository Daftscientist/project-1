from sanic.exceptions import SanicException
import sanic
import datetime
from sanic.handlers import ErrorHandler


class CustomErrorHandler(ErrorHandler):
    def default(
        self, request: sanic.Request, exception: Exception
    ) -> sanic.HTTPResponse:
        """handles errors that have no error handlers assigned"""
        #raise exception
        #status_code = getattr(exception, "status_code", 500)
        try:
            status_code = exception.status_code
        except AttributeError:
            status_code = 500

        logf = open("./localstorage/exceptions.log", "a")
        logf.write(
            f"ID: {str(request.id)} - Message: '{str(exception)}' - Code: {str(status_code)} - Timestamp: {str(datetime.datetime.now())}\n"
        )
        logf.close()
        #print(str(exception), exception.__class__.__name__)
        if "argument after ** must be a mapping, not NoneType" in str(exception) and status_code == 500: #this line is vile
            error_message = "Invalid JSON body"
        else:
            error_message = str(exception)
        

        return sanic.json(
            {
                "error": error_message,
                "success": False,
                "status": status_code,
                "path": request.path,
                "request_id": str(request.id),
                "timestamp": str(datetime.datetime.now()),
            },
            status=status_code,
        )
