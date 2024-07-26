"""
This module contains the NodeDAL class for managing nodes.
"""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# pylint: disable=import-error
from database.models.node import Node

class NodeDAL():
    """
    This class manages nodes in the database.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_node(self, name: str, endpoint_url: str, api_version: str) -> Node:
        """
        Creates a new node in the database.

        Args:
            name (str): The name of the node.
            endpoint_url (str): The endpoint URL of the node.
            api_version (str): The API version of the node.

        Returns:
            None
        """
        new_node = Node(
            name=name,
            endpoint_url=endpoint_url,
            api_version=api_version
        )
        self.db_session.add(new_node)
        await self.db_session.flush()

    async def get_node_by_uuid(self, uuid: int) -> Node:
        """
        Retrieve an node by its UUID.

        Args:
            uuid (int): The UUID of the node.

        Returns:
            Node: The node object matching the given UUID.
        """
        q = await self.db_session.execute(select(Node).where(Node.uuid == uuid))
        return q.scalars().first()

    async def get_all_nodes(self) -> List[Node]:
        """
        Retrieves all nodes from the database.

        Returns:
            A list of Node objects representing all nodes in the database.
        """
        q = await self.db_session.execute(select(Node).order_by(Node.identifier))
        return q.scalars().all()

    async def update_node(
            self,
            uuid: int,
            name: Optional[str] = None,
            endpoint_url: Optional[str] = None,
            api_version: Optional[str] = None
        ):
        """
        Update an node.

        Args:
            uuid (int): The UUID of the node to be updated.
            server_uuid (Optional[str]): The UUID of the server to be assigned to the node.
            ip (Optional[str]): The IP address to be assigned to the node.
            port (Optional[int]): The port number to be assigned to the node.
        """
        q = update(Node).where(Node.uuid == uuid)
        if name:
            q = q.values(name=name)
        if endpoint_url:
            q = q.values(endpoint_url=endpoint_url)
        if api_version:
            q = q.values(api_version=api_version)

        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
