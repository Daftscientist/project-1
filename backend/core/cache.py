from database import db
from database.dals.user_dal import UsersDAL
from typing import Union

CACHED_DATA = dict()
CACHED_EMAIL_TO_UUID = dict()

async def init():
    ''' runs the cache '''
    print("Initilising the cache...")
    print("Adding user data to the cache...")
    async with db.async_session() as session:
        async with session.begin():
            users_dal = UsersDAL(session)
            users = await users_dal.get_all_users()
            for user in users:
                await add(user.identifier, user.uuid, user.email, user.username, user.avatar, user.google_account_identifier, user.discord_account_identifier, user.created_at, None)
    print("Cache initilised.")
    print("Cache contains " + str(len(CACHED_DATA)) + " users.")


async def add(identifier: str, uuid: str, email: str, username: str, avatar: str, google_account_identifier: str, discord_account_identifier: str, created_at: str, session_id: Union[str, None]) -> dict:
    ''' adds a user to the cache '''
    CACHED_DATA[uuid] = {
        "identifier": identifier,
        "uuid": uuid,
        "email": email,
        "username": username,
        "avatar": avatar,
        "google_account_identifier": google_account_identifier,
        "discord_account_identifier": discord_account_identifier,
        "created_at": created_at, 
        "session_id": session_id
    }
    CACHED_EMAIL_TO_UUID[email] = uuid
    return CACHED_DATA[uuid]

async def get(uuid: str) -> dict | None:
    try:
        return CACHED_DATA[uuid]
    except KeyError:
        return None

async def get_uuid(email: str) -> str | None:
    try:
        return CACHED_EMAIL_TO_UUID[email]
    except KeyError:
        return None

async def delete_uuid(uuid: str) -> None:
    try:
        del CACHED_DATA[uuid]
    except KeyError:
        return None

async def delete_user(uuid: str) -> None:
    try:
        del CACHED_DATA[uuid]
        del CACHED_EMAIL_TO_UUID[CACHED_DATA[uuid]["email"]]
    except KeyError:
        return None

async def clear() -> None:
    CACHED_DATA.clear()
    CACHED_EMAIL_TO_UUID.clear()

async def get_all() -> list[dict]:
    return list(CACHED_DATA.values())

async def update(uuid: str, email: str = None, username: str = None, avatar: str = None, google_account_identifier: str = None, discord_account_identifier: str = None, session_id: Union[str, None] = None) -> dict:
    if email:
        del CACHED_EMAIL_TO_UUID[CACHED_DATA[uuid]["email"]]
        CACHED_DATA[uuid]["email"] = email
        CACHED_EMAIL_TO_UUID[email] = uuid
    if username:
        CACHED_DATA[uuid]["username"] = username
    if avatar:
        CACHED_DATA[uuid]["avatar"] = avatar
    if google_account_identifier:
        CACHED_DATA[uuid]["google_account_identifier"] = google_account_identifier
    if discord_account_identifier:
        CACHED_DATA[uuid]["discord_account_identifier"] = discord_account_identifier
    if session_id:
        CACHED_DATA[uuid]["session_id"] = session_id
    return CACHED_DATA[uuid]
