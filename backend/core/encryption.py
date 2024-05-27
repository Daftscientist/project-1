from cryptography.fernet import Fernet
import sanic

fernet = Fernet(
    bytes(
        sanic.Sanic.get_app().config["core"]["encryption_key"],
        "utf-8"
    )
)

def encrypt(string: str) -> bytes:
    """
    Encrypts a string using the Fernet encryption algorithm.

    Args:
        string (str): The string to be encrypted.

    Returns:
        bytes: The encrypted string as bytes.
    """
    return fernet.encrypt(string.encode())

def decrypt(bytes: bytes) -> str:
    """
    Decrypts the given bytes using the Fernet encryption algorithm.

    Args:
        bytes (bytes): The encrypted bytes to be decrypted.

    Returns:
        str: The decrypted string.

    """
    return fernet.decrypt(bytes).decode()