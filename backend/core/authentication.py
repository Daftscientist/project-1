from functools import wraps
from sanic import Unauthorized
import jwt
from core.session import session_data

SECRET_KEY = "23893784023409283964732894790792848932798479012043789247589357838401293890"  ## For testing only. This should be stored in an environment variable.
ALGORITHM = "HS256"
COOKIE_IDENTITY = "session"

def check_for_cookie(request):
    if request.cookies is None:
        return False
    if not COOKIE_IDENTITY in request.cookies: 
        return False
    return True

async def check_authorization(request):
    if not check_for_cookie(request):
        raise Unauthorized("Authentication required.")
    cookie = jwt.decode(request.cookies.get(COOKIE_IDENTITY), SECRET_KEY, algorithms=[ALGORITHM])
    if cookie["session_id"] is None:
        raise Unauthorized("Authentication required.")
    if not cookie["session_id"] in session_data:
        raise Unauthorized("Authentication required.")
    print("hi")
    return True

def protected_method(wrapped): ## fix to fetch the function below
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            print(args, kwargs)
            is_authenticated = await check_authorization(request)

            if not is_authenticated:
                raise Unauthorized("Authentication required.")
            
            response = await f(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator(wrapped)

