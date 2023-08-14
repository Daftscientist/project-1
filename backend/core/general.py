import json
from uuid import UUID
from datetime import date, datetime


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