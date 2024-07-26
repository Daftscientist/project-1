import time
import datetime
import secrets
from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.oauth.github import GitHubOAuth, USER_INFO_URL
from database.dals.user_dal import UsersDAL
from database import db
from core.cookies import check_if_cookie_is_present, check_oauth_cookie_present, del_oauth_cookie, get_oauth_cookie, send_cookie
from core.authentication import protected

def create_session_id():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(16)

class GitHubOauthCallbackView(HTTPMethodView):
    """The GitHub OAuth callback view."""

    @staticmethod
    async def get(request: Request):
        """ The GitHub OAuth callback route. """

        last_login = datetime.datetime.now()

        if not request.app.ctx.config["oauth"]["github"]["enabled"]:
            raise BadRequest("GitHub OAuth is not enabled on this server.")

        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")

        client = GitHubOAuth(
            redirect_uri=request.app.ctx.config["oauth"]["github"]["login_redirect_uri"],
            scopes=request.app.ctx.config["oauth"]["github"]["scopes"],
            client_id=request.app.ctx.config["oauth"]["github"]["client_id"],
            client_secret=request.app.ctx.config["oauth"]["github"]["client_secret"]
        )

        if not check_oauth_cookie_present(request=request, identifier="github_oauth"):
            raise BadRequest("You have not started linking a GitHub account.")

        fetched_data = client.fetch_token(request)

        token = fetched_data[0]
        state = fetched_data[1]

        if token is None or state is None:
            raise BadRequest("Failed to fetch GitHub account information.")

        if state != get_oauth_cookie(request, "github_oauth")["state"]:
            raise BadRequest("Invalid state parameter received from GitHub.")

        details = client.oauth.get(USER_INFO_URL)
        try:
            github_user_info = details.json()
        except Exception:
            raise BadRequest("Failed to fetch GitHub account information.")

        email = github_user_info.get("email")
        github_id = github_user_info.get("id")
        avatar_url = github_user_info.get("avatar_url")

        if email is None or github_id is None:
            raise BadRequest("Failed to fetch GitHub account information.")

        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)

                user_info = await users_dal.get_user_by_github_id(github_id)

                if user_info is None:
                    raise BadRequest("Account does not exist.")

                if github_id != user_info.github_account_identifier:
                    raise BadRequest("Account does not exist.")

                if user_info.max_sessions <= len(await request.app.ctx.session.concurrent_sessions(user_info.uuid)):
                    raise BadRequest("You have too many concurrent sessions.")

                uuid = user_info.uuid

                session_id = create_session_id()

                user_ip = request.remote_addr or request.ip

                await request.app.ctx.session.add(session_id, uuid, user_ip, time.time() + request.app.ctx.SESSION_EXPIRY_IN)
                if not len(await request.app.ctx.session.concurrent_sessions(user_info.uuid)) > 1:
                    await request.app.ctx.cache.update(user_info)

                await users_dal.update_user(uuid=uuid, last_login=last_login, latest_ip=user_ip)

                await request.app.ctx.cache.update(
                    await users_dal.get_user_by_uuid(uuid)
                )

                if user_info.two_factor_authentication_enabled and request.app.ctx.config["2fa"]["enabled"]:
                    await request.app.ctx.session.change_twofactor_auth_state(session_id, True)
                    response = send_cookie(request, "Logged in successfully. Your access is limited until you confirm your 2fa code.", {"session_id": session_id})
                else:
                    response = send_cookie(request, "Logged in successfully.", {"session_id": session_id})

                # Delete the cookie
                response = del_oauth_cookie(response, "github_oauth")

                return response
