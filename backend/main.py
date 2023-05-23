import sanic
import routes
import datetime
from core import cache
from sanic.handlers import ErrorHandler

app = sanic.Sanic("backend")
app.config.FALLBACK_ERROR_FORMAT = "auto"
prefix = routes.routes_v1[0]

cache.init()

class CustomErrorHandler(ErrorHandler):
    def default(self, request: sanic.Request, exception: Exception) -> sanic.HTTPResponse:
        ''' handles errors that have no error handlers assigned '''
        
        try:
            status_code = exception.status_code
        except AttributeError:
            status_code = 500

        logf = open("./localstorage/exceptions.log", "a")
        logf.write(f"ID: {str(request.id)} - Message: '{str(exception)}' - Code: {str(status_code)} - Timestamp: {str(datetime.datetime.now())}\n")
        logf.close()

        return sanic.json({
            "error": str(exception),
            "status": status_code,
            "path": request.path,
            "request_id": str(request.id),
            "timestamp": str(datetime.datetime.now())
        }, status=status_code)

app.error_handler = CustomErrorHandler()

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1],
        uri=f"/{prefix}{route[0]}",
    )