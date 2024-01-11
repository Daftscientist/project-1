import datetime
from typing import List, Optional

from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models.bannedIPs import BannedIPs

class BannedIpsDal():
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def ban_new_ip(self, ip: str, reason: str, ip_of_admin: str):
        """Bans a new IP."""
        new_ban = BannedIPs(ip=ip, reason=reason, ip_of_admin=ip_of_admin)
        self.db_session.add(new_ban)
        await self.db_session.flush()
    
    async def get_banned_ips(self) -> List[BannedIPs]:
        """Returns all banned IPs."""
        return await self.db_session.execute(select(BannedIPs)).scalars().all()
    
    async def check_ip(self, ip: str) -> Optional[BannedIPs]:
        """Checks if an IP is banned."""
        return await self.db_session.execute(select(BannedIPs).where(BannedIPs.ip == ip)).scalar_one_or_none()
    
    async def unban_ip(self, ip: str):
        """deletes the record corresponding to the provided ip in the database."""
        await self.db_session.execute(delete(BannedIPs).where(BannedIPs.ip == ip))
        await self.db_session.flush()

