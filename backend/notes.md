## Useful to know:

`@protected` -> `from core.authentication import protected`
    - Protects a route with cookie checking

`@parse_params(body=CLASSHERE)` -> `from sanic_dantic import parse_params, BaseModel`
    - Allows you to outline a `BaseModel` class,pass this in the decorator and add a route function parameter called params, to recieve params inside the function.

`fix_dict()` -> `from core.general import fix_dict`
    - Returns json data sterilized from a dict

`from database.dals import *` -> `allocation_dal.py` `server_dal.py` `user_dal.py`
    -> Has database management functions

`from database.models import *` -> `allocation.py` `server.py` `user.py`
    - All the models made for the database

error handler -> `from errors import custom_handler`
    - Error handling logic, uncomment the first comment in development

routing -> `import routes`
    - All routing is manual, define in this file.

