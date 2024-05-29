from functools import partial
from typing import Union
from async_oauthlib import OAuth2Session
from sanic import Request, response, Sanic
from core.general import load_config

CLIENT_ID = load_config()["oauth"]["discord"]["client_id"]
CLIENT_SECRET = load_config()["oauth"]["discord"]["client_secret"]

API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"

def make_session(*, token: dict = None, state: dict = None, token_updater = None, redirect_uri) -> OAuth2Session:
    """
    Creates an OAuth2Session object for Discord authentication.

    Args:
        token (dict, optional): The token dictionary to initialize the session with. Defaults to None.
        state (dict, optional): The state dictionary to initialize the session with. Defaults to None.
        token_updater (callable, optional): A callable function to update the token. Defaults to None.
        redirect_uri (str): The redirect URI.

    Returns:
        OAuth2Session: The initialized OAuth2Session object.

    """
    return OAuth2Session(
        client_id=CLIENT_ID,
        token=token,
        state=state,
        redirect_uri=redirect_uri,
        scope=["identify"],
        auto_refresh_kwargs={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        token_updater=token_updater,
        auto_refresh_url=TOKEN_URL,
    )

def token_updater(request: Request, token: dict) -> None:
    """
    Updates the Discord OAuth2 token in the session.

    Args:
        request (Request): The request object.
        token (dict): The updated token dictionary.

    Returns:
        None
    """
    # has to be made into a partial function before use
    request.ctx.session["discord_oauth2_token"] = token

async def generate_oauth_url(redirect_uri, request) -> str:
    """
    Generates the OAuth URL for Discord authentication.

    Returns:
        str: The OAuth URL.

    """

    discord = make_session(token_updater=partial(token_updater, request), redirect_uri=redirect_uri)
    url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    request.ctx.session["discord_oauth2_state"] = state
    return url


async def handle_callback(request: Request, redirect_uri) -> dict:
    """
    Handles the callback from Discord authentication.

    Args:
        request (Request): The request object.

    Returns:
        dict: The token dictionary.

    """
    if request.args.get("error"):
        return False

    discord = make_session(
        state=request.ctx.session.get("discord_oauth2_state"),
        token_updater=partial(token_updater, request),
    )
    token = await discord.fetch_token(
        TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url
    )
    return token

def get_user_info(token: dict, redirect_uri) -> dict:
    """
    Gets the user information from Discord.

    Args:
        token (dict): The token dictionary.

    Returns:
        dict: The user information.

    """
    session = make_session(token=token, redirect_uri=redirect_uri)
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

def check_logged_in(request: Request) -> Union[dict, bool]:
    """Returns the user's token if they finished authentication with discord, else return False."""
    token = request.ctx.session.get("discord_oauth2_token")
    return token if token else False