from cryptography.fernet import Fernet

fernet = Fernet()

def encrypt(string: str) -> bytes:
    """ Takes a string and uses the key provided to encrypt the string. """
    return fernet.encrypt(string.encode())

def decrypt(bytes: bytes) -> str:
    """ Takes bytes and uses the key provided to decrypt the string. """
    return fernet.decrypt(bytes).decode()