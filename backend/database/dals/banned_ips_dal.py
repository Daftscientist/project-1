"""
This module contains the BannedIpsDal class for managing banned IPs.
"""

from typing import List, Optional
from sqlalchemy import delete

from sqlalchemy.future import select
from sqlalchemy.orm import Session

# pylint: disable=import-error
from backend.database.models.banned_ips import BannedIPs

class BannedIpsDal():
    """
    This class represents the data access layer for managing banned IPs.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def ban_new_ip(self, ip: str, reason: str, ip_of_admin: str):
        """
        Bans a new IP.

        Args:
            ip (str): The IP address to be banned.
            reason (str): The reason for banning the IP.
            ip_of_admin (str): The IP address of the admin who banned the IP.
        """
        new_ban = BannedIPs(ip=ip, reason=reason, ip_of_admin=ip_of_admin)
        self.db_session.add(new_ban)
        await self.db_session.flush()

    async def get_banned_ips(self) -> List[BannedIPs]:
        """
        Returns all banned IPs.

        Returns:
            List[BannedIPs]: A list of all banned IPs.
        """
        return await self.db_session.execute(
            select(BannedIPs)
        ).scalars().all()

    async def check_ip(self, ip: str) -> Optional[BannedIPs]:
        """
        Checks if an IP is banned.

        Parameters:
            ip (str): The IP address to check.

        Returns:
            Optional[BannedIPs]: The banned IP object if found, otherwise None.
        """
        return await self.db_session.execute(
            select(BannedIPs).where(BannedIPs.ip == ip)
        ).scalar_one_or_none()

    async def unban_ip(self, ip: str):
        """
        Deletes the record corresponding to the provided IP address in the database.

        Parameters:
        - ip (str): The IP address to be unbanned.

        Returns:
        None
        """
        await self.db_session.execute(
            delete(BannedIPs).where(BannedIPs.ip == ip)
        )
        await self.db_session.flush()
