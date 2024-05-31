"""
This module contains the Mfa_backup_codes_DAL class for accessing server data.
"""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import Session

# pylint: disable=import-error
from database.models.mfa_backup_codes import Mfa_backup_codes

class Mfa_backup_codes_DAL():
    """
    This class represents the Data Access Layer for the mfa backup codes model.
    """
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_backup_code(self, owner_uuid, code: str):
        """
        Create a backup code for the specified user.

        Args:
            owner_uuid: The UUID of the user to create the backup code for.
            code (str): The backup code to create.
        """
        code = Mfa_backup_codes(owner_uuid=owner_uuid, code=code)
        self.db_session.add(code)
        await self.db_session.commit()
        return code

    async def get_users_codes(self, owner_uuid: int) -> List[Mfa_backup_codes]:
        """
        Get all backup codes for the specified user.

        Args:
            owner_uuid: The UUID of the user to get the backup codes for.

        Returns:
            List[Mfa_backup_codes]: A list of backup codes for the specified user.
        """
        q = select(Mfa_backup_codes).where(Mfa_backup_codes.owner_uuid == owner_uuid)
        return await self.db_session.execute(q)

    async def check_if_code_exists(self, owner_uuid: int, code: str) -> Optional[Mfa_backup_codes]:
        """
        Check if a backup code exists for the specified user.

        Args:
            owner_uuid: The UUID of the user to check the backup code for.
            code (str): The backup code to check.

        Returns:
            Optional[Mfa_backup_codes]: The backup code if it exists, otherwise None.
        """
        q = select(Mfa_backup_codes).where(Mfa_backup_codes.owner_uuid == owner_uuid, Mfa_backup_codes.code == code)
        return await self.db_session.execute(q).scalar()

    def delete_users_codes(self, owner_uuid: int):
        """
        Delete all backup codes for the specified user.

        Args:
            owner_uuid: The UUID of the user to delete the backup codes for.
        """
        ## check if the user exists
        if not self.db_session.execute(select(Mfa_backup_codes).where(Mfa_backup_codes.owner_uuid == owner_uuid)).scalar():
            return False

        q = select(Mfa_backup_codes).where(Mfa_backup_codes.owner_uuid == owner_uuid)
        self.db_session.execute(q).delete()
        self.db_session.commit()
        return True

    async def delete_code(self, owner_uuid: int, code: str):
        """
        Delete a backup code for the specified user.

        Args:
            owner_uuid: The UUID of the user to delete the backup code for.
            code (str): The backup code to delete.
        """
        q = select(Mfa_backup_codes).where(Mfa_backup_codes.owner_uuid == owner_uuid, Mfa_backup_codes.code == code)
        self.db_session.execute(q).delete()
        self.db_session.commit()
        return True
    