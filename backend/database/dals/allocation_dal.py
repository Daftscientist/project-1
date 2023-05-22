from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models.allocation import Allocation

class AllocationsDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_Allocation(self, ip: str, port: int, node_identifier: int):
        new_allocation = Allocation(ip=ip, port=port, node_identifier=node_identifier)
        self.db_session.add(new_allocation)
        await self.db_session.flush()

    async def get_allocation_by_uuid(self, uuid: int) -> Allocation:
        q = await self.db_session.execute(select(Allocation).where(Allocation.uuid == uuid))
        return q.scalars().first()

    async def get_all_allocations(self) -> List[Allocation]:
        q = await self.db_session.execute(select(Allocation).order_by(Allocation.identifier))
        return q.scalars().all()

    async def update_Allocation(self, uuid: int, allocationname: Optional[str] = None, server_uuid: Optional[str] = None, ip: Optional[str] = None, port: Optional[int] = None):
        q = update(Allocation).where(Allocation.uuid == uuid)
        if allocationname:
            q = q.values(allocationname=allocationname)
        if server_uuid:
            q = q.values(server_uuid=server_uuid)
        if ip:
            q = q.values(ip=ip)
        if port:
            q = q.values(port=port)
        
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)