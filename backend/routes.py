from views import index, hello
from views.auth import create, logout, login

routes_v1 = [
    "api/v1", ## route prefix
    [
        ["/", index.IndexView.as_view()],
        ["/hello", hello.HelloView.as_view()],
        ["/auth/create", create.CreateView.as_view()],
        ["/auth/login", login.LoginView.as_view()],
        ["/auth/logout", logout.LogoutView.as_view()]
    ]
]