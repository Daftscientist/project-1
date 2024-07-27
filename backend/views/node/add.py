from sanic import Request
from core.responses import success
from sanic.views import HTTPMethodView

class NodeAddView(HTTPMethodView):
    """The NodeAddView view."""


## setup admin decorator and admin perms first