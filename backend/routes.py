from views import index, hello
from views.user import create, logout

routes_v1 = [
    "api/v1", ## route prefix
    [
        ["/", index.IndexView.as_view()],
        ["/hello", hello.HelloView.as_view()],
        ["/user/create", create.CreateView.as_view()],
        ["/user/logout", logout.LogoutView.as_view()]
    ]
]