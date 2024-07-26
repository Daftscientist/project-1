from sanic import Request, BadRequest, redirect
from sanic.views import HTTPMethodView
from core.oauth.google import GoogleOAuth
from core.cookies import check_if_cookie_is_present, check_oauth_cookie_present, send_oauth_cookie
#from core.authentication import protected

class GoogleOauthView(HTTPMethodView):
    """The Google OAuth view."""

    @staticmethod
    async def get(request: Request):
        """ The Google OAuth route. """

        if not request.app.ctx.config["oauth"]["google"]["enabled"]:
            raise BadRequest("Google OAuth is not enabled on this server.")
        
        if await check_if_cookie_is_present(request):
            raise BadRequest("You are already logged in.")
    
        if check_oauth_cookie_present(request=request, identifier="google_oauth"):
            raise BadRequest("You are already linking a Google account.")
        
        client = GoogleOAuth(
            redirect_uri=request.app.ctx.config["oauth"]["google"]["login_redirect_uri"],
            scopes=request.app.ctx.config["oauth"]["google"]["scopes"],
            client_id=request.app.ctx.config["oauth"]["google"]["client_id"],
            client_secret=request.app.ctx.config["oauth"]["google"]["client_secret"]
        )

        login_info = client.get_login_url()
        redirect_uri = login_info[0]

        response = redirect(redirect_uri)
        response = send_oauth_cookie(
            request=request,
            response=response, 
            identifier="google_oauth",
            data={
                "state": login_info[1]
            }
        )
        return response
