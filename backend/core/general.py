"""
This module provides general utility functions.
"""
import json
from uuid import UUID
from datetime import date, datetime
import uuid
# pylint: disable=import-error
from database.dals.user_dal import UsersDAL
from database import db


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
