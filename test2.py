from functools import wraps
from sanic import Sanic
from sanic import response as res

app = Sanic(__name__)

app.ctx.hello = 'world'

def inject_cached_user():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            user = request.app.ctx.hello
            return await f(request, user, *args, **kwargs)
        return decorated_function
    return decorator

@app.route("/")
@inject_cached_user()
async def test(req, user):
    print(req, user)
    return res.text("I\'m a teapot", status=418)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
