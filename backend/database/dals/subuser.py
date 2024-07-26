"""
This module contains the SubuserDAL class for managing subusers.
"""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# pylint: disable=import-error
from database.models.subuser import Subuser

class SubuserDAL():
    """
    This class manages subusers in the database.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_subuser(self, name: str, endpoint_url: str, api_version: str) -> Subuser:
        """
        Creates a new subuser in the database.

        Args:
            name (str): The name of the subuser.
            endpoint_url (str): The endpoint URL of the subuser.
            api_version (str): The API version of the subuser.

        Returns:
            None
        """
        new_subuser = Subuser(
            name=name,
            endpoint_url=endpoint_url,
            api_version=api_version
        )
        self.db_session.add(new_subuser)
        await self.db_session.flush()

    async def get_subuser_by_uuid(self, uuid: int) -> Subuser:
        """
        Retrieve an subuser by its UUID.

        Args:
            uuid (int): The UUID of the subuser.

        Returns:
            Subuser: The subuser object matching the given UUID.
        """
        q = await self.db_session.execute(select(Subuser).where(Subuser.uuid == uuid))
        return q.scalars().first()

    async def get_all_subusers(self) -> List[Subuser]:
        """
        Retrieves all subusers from the database.

        Returns:
            A list of Subuser objects representing all subusers in the database.
        """
        q = await self.db_session.execute(select(Subuser).order_by(Subuser.identifier))
        return q.scalars().all()

    async def update_subuser(
            self,
            uuid: int,
            name: Optional[str] = None,
            endpoint_url: Optional[str] = None,
            api_version: Optional[str] = None
        ):
        """
        Update an subuser.

        Args:
            uuid (int): The UUID of the subuser to be updated.
            server_uuid (Optional[str]): The UUID of the server to be assigned to the subuser.
            ip (Optional[str]): The IP address to be assigned to the subuser.
            port (Optional[int]): The port number to be assigned to the subuser.
        """
        q = update(Subuser).where(Subuser.uuid == uuid)
        if name:
            q = q.values(name=name)
        if endpoint_url:
            q = q.values(endpoint_url=endpoint_url)
        if api_version:
            q = q.values(api_version=api_version)

        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
