from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models.server import Server

class ServerDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def create_server(self, name: str, node_identifier: int, cpu_limit: int, memory_limit: int, disk_limit: int, swap_limit: int, io_limit: int, threads_limit: int, database_limit: int, backups_limit: int, server_type: int):
        new_server = Server(name=name, node_identifier=node_identifier, cpu_limit=cpu_limit, memory_limit=memory_limit, disk_limit=disk_limit, swap_limit=swap_limit, io_limit=io_limit, threads_limit=threads_limit, database_limit=database_limit, backups_limit=backups_limit, server_type=server_type)
        self.db_session.add(new_server)
        await self.db_session.flush()
    
    async def get_server_by_uuid(self, uuid: int) -> Server:
        q = await self.db_session.execute(select(Server).where(Server.uuid == uuid))
        return q.scalars().first()
    
    async def get_all_servers(self) -> List[Server]:
        q = await self.db_session.execute(select(Server).order_by(Server.identifier))
        return q.scalars().all()
    
    async def update_server(self, uuid: int, name: Optional[str] = None, node_identifier: Optional[int] = None, cpu_limit: Optional[int] = None, memory_limit: Optional[int] = None, disk_limit: Optional[int] = None, swap_limit: Optional[int] = None, io_limit: Optional[int] = None, threads_limit: Optional[int] = None, database_limit: Optional[int] = None, backups_limit: Optional[int] = None, server_type: Optional[int] = None, installed: Optional[bool] = None):
        q = update(Server).where(Server.uuid == uuid)
        if name:
            q = q.values(name=name)
        if node_identifier:
            q = q.values(node_identifier=node_identifier)
        if cpu_limit:
            q = q.values(cpu_limit=cpu_limit)
        if memory_limit:
            q = q.values(memory_limit=memory_limit)
        if disk_limit:
            q = q.values(disk_limit=disk_limit)
        if swap_limit:
            q = q.values(swap_limit=swap_limit)
        if io_limit:
            q = q.values(io_limit=io_limit)
        if threads_limit:
            q = q.values(threads_limit=threads_limit)
        if database_limit:
            q = q.values(database_limit=database_limit)
        if backups_limit:
            q = q.values(backups_limit=backups_limit)
        if server_type:
            q = q.values(server_type=server_type)
        if installed:
            q = q.values(installed=installed)
        
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
    