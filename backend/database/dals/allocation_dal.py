"""
This module contains the AllocationsDAL class for managing allocations.
"""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# pylint: disable=import-error
from database.models.allocation import Allocation

class AllocationsDAL():
    """
    This class manages allocations in the database.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_allocation(self, ip: str, port: int, node_identifier: int):
        """
        Creates a new allocation in the database.

        Args:
            ip (str): The IP address of the allocation.
            port (int): The port number of the allocation.
            node_identifier (int): The identifier of the node.

        Returns:
            None
        """
        new_allocation = Allocation(ip=ip, port=port, node_identifier=node_identifier)
        self.db_session.add(new_allocation)
        await self.db_session.flush()

    async def get_allocation_by_uuid(self, uuid: int) -> Allocation:
        """
        Retrieve an allocation by its UUID.

        Args:
            uuid (int): The UUID of the allocation.

        Returns:
            Allocation: The allocation object matching the given UUID.
        """
        q = await self.db_session.execute(select(Allocation).where(Allocation.uuid == uuid))
        return q.scalars().first()

    async def get_all_allocations(self) -> List[Allocation]:
        """
        Retrieves all allocations from the database.

        Returns:
            A list of Allocation objects representing all allocations in the database.
        """
        q = await self.db_session.execute(select(Allocation).order_by(Allocation.identifier))
        return q.scalars().all()

    async def update_allocation(
            self,
            uuid: int,
            server_uuid: Optional[str] = None,
            ip: Optional[str] = None,
            port: Optional[int] = None
        ):
        """
        Update an allocation.

        Args:
            uuid (int): The UUID of the allocation to be updated.
            server_uuid (Optional[str]): The UUID of the server to be assigned to the allocation.
            ip (Optional[str]): The IP address to be assigned to the allocation.
            port (Optional[int]): The port number to be assigned to the allocation.
        """
        q = update(Allocation).where(Allocation.uuid == uuid)
        if server_uuid:
            q = q.values(server_uuid=server_uuid)
        if ip:
            q = q.values(ip=ip)
        if port:
            q = q.values(port=port)

        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
