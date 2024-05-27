from views import index, hello
from views.auth import create, logout, login
from views.account.get import GetUserView
from views.account.edit import avatar, email, password, username
from views.account.session.get import GetActiveSessionsView
from views.account.session.delete import DeleteSessionView
from views.account.edit.max_sessions import UpdateMaxSessions
from views.auth.oauth.discord import DiscordOauthView
from views.auth.callback import discord


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

        # --- Account --- 
        ["/account/get", GetUserView],
        ["/account/edit/username", username.UpdateUsernameView],
        ["/account/edit/email", email.UpdateEmailView],
        ["/account/edit/password", password.UpdatePasswordView],
        ["/account/edit/avatar", avatar.UpdateAvatarView],
        ["/account/edit/max-sessions", UpdateMaxSessions],

        # --- Sessions --- 
        ["/account/session/get/all", GetActiveSessionsView],
        ["/account/session/delete", DeleteSessionView],

        # --- Callback ---
        ["/auth/oauth/callback/discord", discord.DiscordOauthCallbackView]


    ]
]

"""
- Versioning:
-> To create a new api version, add a new list to the routes list. 
   This will automatically become one version after the last - while the other can still function as normal.
-> To add a new route, add a new list to the version list.
   The first item in the list is the route, the second is the view.
"""