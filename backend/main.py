import sanic
import routes

app = sanic.Sanic(__name__)

prefix = routes.routes_v1[0]

for route in routes.routes_v1[1]:
    app.add_route(
        handler=route[1][1], 
        uri="/" + prefix + route[0],
        methods=route[1][0]
    )
