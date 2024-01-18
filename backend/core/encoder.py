"""
This module provides functions for hashing and checking passwords using bcrypt.
"""

import aiobcrypt

async def hash_password(password: bytes) -> str:
    """
    Hashes the given password using bcrypt.

    Args:
        password (bytes): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    salt = await aiobcrypt.gensalt()

    hashed_password = await aiobcrypt.hashpw(password, salt)
    return hashed_password

async def check_password(password: bytes, hashed_password: bytes) -> bool:
    """
    Check if the provided password matches the hashed password.

    Args:
        password (bytes): The password to check.
        hashed_password (bytes): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    if await aiobcrypt.checkpw(password, hashed_password):
        return True
    return False
