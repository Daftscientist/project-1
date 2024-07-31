from sanic import Request
from database import db
from database.dals.server_dal import ServerDAL
from database.models.user import User
from core.authentication import protected
from core.general import inject_cached_user, restricted_to_verified
from core.responses import success
from sanic.views import HTTPMethodView
from sanic_dantic import parse_params, BaseModel
from sanic import BadRequest
from core.incus.manager import IncusManager

class InstanceStartView(HTTPMethodView):
    """The ServerStartView view."""

    class StartInstanceRequest(BaseModel):
        """The create user request model."""

        server_uuid: str
        forced: bool = False
        timeout: int = 0

    @staticmethod
    @protected
    @inject_cached_user()
    @restricted_to_verified()
    @parse_params(body=StartInstanceRequest)
    async def post(request: Request, user: User, params: StartInstanceRequest):
        """The start instance route."""

        async with db.async_session() as session:
            async with session.begin():
                servers_dal = ServerDAL(session)

                server_uuid_int = int(params.server_uuid, 16)


                server = await servers_dal.get_server_by_uuid(server_uuid_int)
                if not server or server == None:
                    raise BadRequest("Server not found.")
                
                if server.owner_id != user.id:
                    raise BadRequest("You are not the owner of this server.")
                
                if not server.installed:
                    raise BadRequest("Server has not finished installing yet.")

                
                manager = IncusManager()
                node = await manager.get_node(server.node_uuid)

                instance = node.get_instance(server.uuid)

                if not instance:
                    raise BadRequest("Instance not found.")
                
                if instance.status == "running":
                    raise BadRequest("Instance is already running.")
                
                if instance.status == "starting":
                    raise BadRequest("Instance is already starting.")
                
                if instance.status == "stopping":
                    raise BadRequest("Instance is stopping.")
                
                await instance.start(forced=params.forced, timeout=params.timeout)

        return await success(request, "Server started successfully.")
