import aiobcrypt

async def hash_password(password: bytes) -> str:
    """Hashes a password."""
    
    salt = await aiobcrypt.gensalt()

    # Generate hashed password
    hashed_password = await aiobcrypt.hashpw(password, salt)
    return hashed_password

async def check_password(password: bytes, hashed_password: bytes) -> bool:
    if await aiobcrypt.checkpw(password, hashed_password):
        return True
    return False