from async_oauthlib import OAuth2Session
from sanic import Request, response, Sanic

CLIENT_ID = Sanic.get_app("app").config["oauth"]["discord"]["client_id"]
CLIENT_SECRET = Sanic.get_app("app").config["oauth"]["discord"]["client_secret"]
REDIRECT_URI = Sanic.get_app("app").config["oauth"]["discord"]["redirect_uri"]

API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"

def make_session(*, token: dict = None, state: dict = None, token_updater = None) -> OAuth2Session:
    """
    Creates an OAuth2Session object for Discord authentication.

    Args:
        token (dict, optional): The token dictionary to initialize the session with. Defaults to None.
        state (dict, optional): The state dictionary to initialize the session with. Defaults to None.
        token_updater (callable, optional): A callable function to update the token. Defaults to None.

    Returns:
        OAuth2Session: The initialized OAuth2Session object.

    """
    return OAuth2Session(
        client_id=CLIENT_ID,
        token=token,
        state=state,
        redirect_uri=REDIRECT_URI,
        scope=["identify"],
        auto_refresh_kwargs={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        token_updater=token_updater,
        auto_refresh_url=TOKEN_URL,
    )

def generate_oauth_url() -> str:
    """
    Generates the OAuth URL for Discord authentication.

    Returns:
        str: The OAuth URL.

    """
    return make_session().authorization_url(AUTHORIZATION_BASE_URL)[0]

def handle_callback(request: Request) -> dict:
    """
    Handles the callback from Discord authentication.

    Args:
        request (Request): The request object.

    Returns:
        dict: The token dictionary.

    """
    session = make_session(state=request.args["state"])
    token = session.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)
    return token

def get_user_info(token: dict) -> dict:
    """
    Gets the user information from Discord.

    Args:
        token (dict): The token dictionary.

    Returns:
        dict: The user information.

    """
    session = make_session(token=token)
    user_info = session.get(API_BASE_URL + "/users/@me").json()
    return user_info

def get_user_avatar(user_info: dict) -> str:
    """
    Gets the user avatar from the user information.

    Args:
        user_info (dict): The user information.

    Returns:
        str: The user avatar URL.

    """
    return f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"

def get_user_id(user_info: dict) -> str:
    """
    Gets the user ID from the user information.

    Args:
        user_info (dict): The user information.

    Returns:
        str: The user ID.

    """
    return user_info["id"]

def get_user_email(user_info: dict) -> str:
    """
    Gets the user email from the user information.

    Args:
        user_info (dict): The user information.

    Returns:
        str: The user email.

    """
    return user_info["email"]