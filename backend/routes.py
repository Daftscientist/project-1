from views import index, hello
from views.auth import create, logout, login
from views.account.get import GetUserView
from views.account.edit import avatar, email, password, username
from views.account.session.get import GetActiveSessionsView
from views.account.session.delete import DeleteSessionView
from views.account.edit.max_sessions import UpdateMaxSessions
from views.auth.oauth.discord import DiscordOauthView
from views.auth.oauth.callback.discord import DiscordOauthCallbackView
from views.account.link.discord import DiscordOauthLinkingView
from views.account.link.callback.discord import DiscordOauthLinkCallbackView
from views.account.verify.email import VerifyEmailView
from views.auth.reset.password import ResetPasswordView
from views.auth.reset.callback.password import ResetPasswordCallbackView

routes = [
    [ # This is version 1
        # --- General ---
        ["/", index.IndexView],
        ["/hello", hello.HelloView],

        # --- Authentication --- 
        ["/auth/create", create.CreateView],
        ["/auth/login", login.LoginView],
        ["/auth/oauth/discord", DiscordOauthView],
        ["/auth/logout", logout.LogoutView],
        ["auth/reset/password", ResetPasswordView],

        # --- Account --- 
        ["/account/get", GetUserView],
        ["/account/verify/email/<identifier>", VerifyEmailView],
        ["/account/edit/username", username.UpdateUsernameView],
        ["/account/edit/email", email.UpdateEmailView],
        ["/account/edit/password", password.UpdatePasswordView],
        ["/account/edit/avatar", avatar.UpdateAvatarView],
        ["/account/edit/max-sessions", UpdateMaxSessions],
        ["/account/link/discord", DiscordOauthLinkingView],

        # --- Sessions --- 
        ["/account/session/get/all", GetActiveSessionsView],
        ["/account/session/delete", DeleteSessionView],        

        # --- Account Callback ---
        ["/account/link/discord/callback", DiscordOauthLinkCallbackView],

        # --- Authentication Callback ---
        ["/auth/oauth/callback/discord", DiscordOauthCallbackView],
        ["/auth/reset/callback/password", ResetPasswordCallbackView],

    ]
]

"""
- Versioning:
-> To create a new api version, add a new list to the routes list. 
   This will automatically become one version after the last - while the other can still function as normal if enabled in the config.
-> Multiple versions can be ran at once, to allow for redundancy - configure this in config.yml.
-> To add a new route, add a new list to the version list.
   The first item in the list is the route, the second is the view.
"""
