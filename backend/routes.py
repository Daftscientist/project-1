from views import index, hello
from views.auth import create, logout, login
from views.account.get import GetUserView
from views.account.edit import avatar, email, password, username

routes_v1 = [
    "api/v1", ## route prefix
    [
        ["/", index.IndexView.as_view()],
        ["/hello", hello.HelloView.as_view()],
        ["/auth/create", create.CreateView.as_view()],
        ["/auth/login", login.LoginView.as_view()],
        ["/auth/logout", logout.LogoutView.as_view()],

        ["/account/get", GetUserView.as_view()],

        ["/account/edit/username", username.UpdateUsernameView.as_view()],
        ["/account/edit/email", email.UpdateEmailView.as_view()],
        ["/account/edit/password", password.UpdatePasswordView.as_view()],
        ["/account/edit/avatar", avatar.UpdateAvatarView.as_view()],
    ]
]