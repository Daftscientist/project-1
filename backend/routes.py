from api import index, hello
from api.user import create

routes_v1 = [
    "api/v1", ## route prefix
    [
        ["/", [("GET", "POST"), index.index_route]],
        ["/hello", [("GET", "POST", "PUT", "HEAD", "OPTIONS", "PATCH", "DELETE"), hello.hello_route]],
        ["/user/create", [("POST",), create.create_user_route]]
    ]
]