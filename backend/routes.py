from views.auth.oauth.callback.google import GoogleOauthCallbackView
from views.auth.oauth.google import GoogleOauthView
from views.auth.verify.backup_code import BackupCodeVerificationView
from views.auth.verify.otp_code import TwoFaVerifyLoginView
from views.account.disable.two_factor_authentication import DisableTwoFaView
from views.account.enable.two_factor_authentication import TwoFaSetupView
from views.account.verify.two_factor_authentication import TwoFaSetupVerificationView
from views.auth.oauth.callback.email import EmailAuthenticationCallbackView
from views.auth.oauth.email import EmailAuthenticationView
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
        ["/auth/logout", logout.LogoutView],
        ["/auth/reset/password", ResetPasswordView],
        ["/auth/oauth/discord", DiscordOauthView],
        ["/auth/oauth/google", GoogleOauthView],
        ["/auth/oauth/email/", EmailAuthenticationView],

        # --- Authentication Verify ---
        ["/auth/verify/backup-code", BackupCodeVerificationView],
        ["/auth/verify/otp-code", TwoFaVerifyLoginView],

        # --- Account --- 
        ["/account/get", GetUserView],
        ["/account/edit/username", username.UpdateUsernameView],
        ["/account/edit/email", email.UpdateEmailView],
        ["/account/edit/password", password.UpdatePasswordView],
        ["/account/edit/avatar", avatar.UpdateAvatarView],
        ["/account/edit/max-sessions", UpdateMaxSessions],
        ["/account/link/discord", DiscordOauthLinkingView],
        ["/account/verify/email/<identifier>", VerifyEmailView],
        ["/account/enable/two-factor-authentication", TwoFaSetupView],
        ["/account/verify/two-factor-authentication", TwoFaSetupVerificationView],
        ["/account/disable/two-factor-authentication", DisableTwoFaView],

        # --- Sessions --- 
        ["/account/session/get/all", GetActiveSessionsView],
        ["/account/session/delete", DeleteSessionView],        

        # --- Account Callback ---
        ["/account/link/callback/discord", DiscordOauthLinkCallbackView],

        # --- Authentication Callback ---
        ["/auth/oauth/callback/discord", DiscordOauthCallbackView],
        ["/auth/oauth/callback/google", GoogleOauthCallbackView],
        ["/auth/oauth/callback/email/<identifier>", EmailAuthenticationCallbackView],
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
