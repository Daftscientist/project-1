import datetime
from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models.BannedIPs import BannedIPs

class UsersDAL():
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def ban_new_ip(self, ip: str, reason: str, ip_of_admin: str):
        """Bans a new IP."""
        new_ban = BannedIPs(ip=ip, reason=reason, ip_of_admin=ip_of_admin)
        self.db_session.add(new_ban)
        await self.db_session.flush()
    

