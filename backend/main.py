import sanic
import routes
import datetime

app = sanic.Sanic("backend")

app.config.FALLBACK_ERROR_FORMAT = "auto"

prefix = routes.routes_v1[0]

from sanic.handlers import ErrorHandler

class CustomErrorHandler(ErrorHandler):
    def default(self, request: sanic.Request, exception: Exception) -> sanic.HTTPResponse:
        ''' handles errors that have no error handlers assigned '''
        return sanic.json({
            "error": str(exception),
            "status": exception.status_code,
            "path": request.path,
            "request_id": str(request.id),
            "timestamp": str(datetime.datetime.now())
        }, status=exception.status_code)

app.error_handler = CustomErrorHandler()

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1][1], 
        uri="/" + prefix + route[0],
        methods=route[1][0]
    )
