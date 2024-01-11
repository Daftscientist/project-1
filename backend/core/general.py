import json
from typing import Iterable
from uuid import UUID
from datetime import date, datetime
import uuid

from database.dals.user_dal import UsersDAL
from database import db

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.__str__()
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        
        return json.JSONEncoder.default(self, obj)

def fix_dict(dict):
    first = json.dumps(dict, cls=UUIDEncoder)
    return json.loads(first)

async def populate_cache(app):
    ## make a list of every individual user with a session and add them to the cache
    for user_uuid in await app.ctx.session.get_all_users():
        user_uuid = uuid.UUID(user_uuid[0])
        async with db.async_session() as session:
            async with session.begin():
                users_dal = UsersDAL(session)
                db_user = await users_dal.get_user_by_uuid(user_uuid)
                await app.ctx.cache.add(db_user)