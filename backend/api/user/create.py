from sanic import Request, text, BadRequest
import re
from database.dals.user_dal import UsersDAL
from sanic_dantic import parse_params, BaseModel
from database import db

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class CreateUserRequest(BaseModel):
    """The create user request model."""

    username: str
    email: str
    password: str



@parse_params(body=CreateUserRequest)
async def create_user_route(request: Request, params: CreateUserRequest):
    """The create user route."""

    ## data validation
    if len(params.username) < 3:
        raise BadRequest("Username must be at least 3 characters long.")
    if len(params.password) < 8:
        raise BadRequest("Password must be at least 8 characters long.")
    if not EMAIL_REGEX.fullmatch(params.email):
        raise BadRequest("Email must be a valid email address.")

    ## create user
    async with db.async_session() as session:
        async with session.begin():
            users_dal = UsersDAL(session)
            return await users_dal.create_user(params.username, params.email, params.password)

    return text(f"OK, this is the create user route. {params.username}")
