"""
This module provides general utility functions.
"""
from functools import wraps
import json
from uuid import UUID
from datetime import date, datetime
import uuid

from sanic import BadRequest, Unauthorized
import yaml
# pylint: disable=import-error
from database.dals.user_dal import UsersDAL
from database import db
from core import email
import secrets

def generate_backup_code(length):
    """
    Generates a backup code.

    Returns:
        str: The generated backup code.
    """

    return secrets.token_hex(int(length / 2)) # prevent odd numbers

def inject_cached_user():
    """
    Decorator function that injects the cached user into the decorated function.

    This decorator retrieves the user from the cache based on the request and injects it as an argument
    into the decorated function. The decorated function can then access the user object.

    Args:
        request: The request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        The decorated function.

    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            user = await request.app.ctx.cache.get(request)
            return await f(request, user, *args, **kwargs)
        return decorated_function
    return decorator

def restricted_to_verified():
    """
    Decorator function that restricts access to verified users only.

    This decorator checks if the user is verified and raises an error if they are not.

    Args:
        request: The request object.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        The decorated function.

    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            user = await request.app.ctx.cache.get(request)
            if not user.email_verified:
                raise BadRequest("Email not verified.")
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator


class UUIDEncoder(json.JSONEncoder):
    """
    JSON encoder that handles UUID, date, and datetime objects.
    """
    def default(self, o):
        if isinstance(o, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(o)
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, bytes):
            return o.decode('utf-8')  # or 'latin-1' or 'iso-8859-1' depending on your data - we use utf-8 (if it is changed, change here)

        return super().default(o)

def fix_dict(dictionary):
    """
    Fixes a dictionary by converting it to a JSON string and then parsing it back to a dictionary.

    Args:
        dictionary (dict): The dictionary to be fixed.

    Returns:
        dict: The fixed dictionary.
    """
    first = json.dumps(dictionary, cls=UUIDEncoder)
    return json.loads(first)

async def populate_cache(app):
    """
    Populates the cache with every individual user with a session.

    Args:
        app: The application object.

    Returns:
        None
    """
    ## make a list of every individual user with a session and add them to the cache
    for user_uuid in await app.ctx.session.get_all_users():
        user_uuid = uuid.UUID(user_uuid[0])
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                db_user = await users_dal.get_user_by_uuid(user_uuid)
                await app.ctx.cache.add(db_user)

def load_config(file_path: str = "config.yml"):
    """
    Loads a yaml config file.

    Args:
        file_path (str): The path to the config file.

    Returns:
        dict: The config file.
    """
    with open(file_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def send_welcome_email(request):
    """
    Sends a welcome email to the user's email address.

    Args:
        request: The request object containing the application context.

    Returns:
        None
    """
    app = request.app
    config = app.ctx.config
    user = app.ctx.cache.get(request.ctx.user.uuid)

    welcome_email = email.Email(
        host=config["email"]["host"],
        port=config["email"]["port"],
        plain_body=config["email"]["welcome_email"]["plain_body"],
        html_body="email/" + config["email"]["welcome_email"]["html_body_file"],
        format_variables={
            "username": user.username,
            "avatar": user.avatar if user.avatar else config["core"]["default_avatar"],
        }
    )
    welcome_email.send(
        sender=config["email"]["sender"],
        recipient=user.email,
        subject=config["email"]["welcome_email"]["subject"]
    )

def send_verification_email(request):
    """
    Sends a verification email to the user's email address.

    Args:
        request: The request object containing the application context.

    Returns:
        None
    """
    app = request.app
    config = app.ctx.config
    user = app.ctx.cache.get(request.ctx.user.uuid)

    verification_email = email.Email(
        host=config["email"]["host"],   
        port=config["email"]["port"],
        plain_body=config["email"]["verification_email"]["plain_body"],
        html_body="email/" + config["email"]["verification_email"]["html_body_file"],
        format_variables={
            "username": user.username,
            "verification_code": user.email_verification_code,
            "verification_url": app.url_for('VerifyEmailView', identifier=user.email_verification_code, _external=True),
            "avatar": user.avatar if user.avatar else config["core"]["default_avatar"],
        }
    )
    verification_email.send(
        sender=config["email"]["sender"],
        recipient=user.email,
        subject=config["email"]["verification_email"]["subject"]
    )

def send_login_email(request, user):
    """
    Sends a login email to the user's email address.

    Args:
        request: The request object containing the application context.
        user: The user object.

    Returns:
        None
    """
    app = request.app
    config = app.ctx.config

    login_email = email.Email(
        host=config["email"]["host"],
        port=config["email"]["port"],
        plain_body=config["email"]["login_email"]["plain_body"],
        html_body="email/" + config["email"]["login_email"]["html_body_file"],
        format_variables={
            "username": user.username,
            "avatar": user.avatar if user.avatar else config["core"]["default_avatar"],
            "login_url": app.url_for('EmailLoginView', identifier=user.login_email_code, _external=True),
        }
    )
    login_email.send(
        sender=config["email"]["sender"],
        recipient=user.email,
        subject=config["email"]["login_email"]["subject"]
    )

def send_password_reset_email(request, user):
    """
    Sends a password reset email to the user's email address.

    Args:
        request: The request object containing the application context.
        user: The user object.

    Returns:
        None
    """
    app = request.app
    config = app.ctx.config

    password_reset_email = email.Email(
        host=config["email"]["host"],
        port=config["email"]["port"],
        plain_body=config["email"]["password_reset_email"]["plain_body"],
        html_body="email/" + config["email"]["password_reset_email"]["html_body_file"],
        format_variables={
            "username": user.username,
            "password_reset_code": user.password_reset_code,
            "password_reset_url": app.url_for('ResetPasswordView', identifier=user.password_reset_code, _external=True),
            "avatar": user.avatar if user.avatar else config["core"]["default_avatar"],
        }
    )
    password_reset_email.send(
        sender=config["email"]["sender"],
        recipient=user.email,
        subject=config["email"]["password_reset_email"]["subject"]
    )