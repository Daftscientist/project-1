"""
This module contains the User model.
"""
import datetime
import os
import uuid
import pyotp
from sqlalchemy import (
    Column,
    Integer,
    String,
    Uuid,
    DateTime,
    Boolean
)
import yaml
# pylint: disable=import-error
from database.db import Base
from sqlalchemy_utils import EncryptedType, StringEncryptedType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def generate_uuid():
    """
    Generate a unique UUID.

    Returns:
        uuid: A generated UUID.
    """

    ouruuid = uuid.uuid4()
    return ouruuid

def load_config(file_path: str = os.getcwd() + "/config.yml"):
    """
    Loads the configuration file.

    Args:
        file_path (str): The path to the configuration file. Default is "config.yml".

    Returns:
        dict: The configuration dictionary.
    """
    with open(file_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

config_data = load_config()

def get_encryption_key():
    """
    Retrieves the encryption key used for encrypting sensitive data.

    Returns:
        bytes: The encryption key as bytes.
    """

    return bytes(
        config_data["core"]["encryption_key"],
        "utf-8"
    )

class User(Base):
    """
    Represents a user in the users table.
    """

    __tablename__ = 'User'

    identifier = Column(Integer, nullable=False, autoincrement=True, unique=True, primary_key=True)
    uuid = Column(Uuid, nullable=False, default=generate_uuid())
    username = Column(String, nullable=False)
    email = Column(
        StringEncryptedType(
            String,
            get_encryption_key(),
            AesEngine
        ), nullable=False
    )
    email_verified = Column(Boolean, nullable=False, default=False)
    email_verification_code = Column(
        StringEncryptedType(
            UUIDType(binary=False),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=generate_uuid()
    )
    login_email_code = Column(
        StringEncryptedType(
            UUIDType(binary=False),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    login_email_code_expiration = Column(
        StringEncryptedType(
            DateTime(timezone=True),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    password = Column(String, nullable=False) #
    password_reset_code = Column(
        StringEncryptedType(
            UUIDType(binary=False),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    password_reset_code_expiration = Column(
        StringEncryptedType(
            DateTime(timezone=True),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    avatar = Column(
        StringEncryptedType( ## future-proofing with string storage of encrypted data
            String,
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    last_login = Column(
        StringEncryptedType(
            DateTime(timezone=True),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    latest_ip = Column(
        StringEncryptedType(
            String(225),
            get_encryption_key(),
            AesEngine
        ), nullable=False, default=None
    )
    signup_ip = Column(
        StringEncryptedType(
            String(225),
            get_encryption_key(),
            AesEngine
        ), nullable=False, default=None
    )
    max_sessions = Column(Integer, nullable=False, default=config_data['session']['user_max_sessions'])
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())
    google_account_identifier = Column(
        StringEncryptedType(
            String(255),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    
    )
    discord_account_identifier = Column(
        StringEncryptedType(
            String(18),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    github_account_identifier = Column(
        StringEncryptedType(
            String(255),
            get_encryption_key(),
            AesEngine
        ), nullable=True, default=None
    )
    two_factor_authentication_enabled = Column(Boolean, nullable=False, default=False)
    two_factor_authentication_secret = Column(
        StringEncryptedType(
            String(255),
            get_encryption_key(),
            AesEngine
        ), nullable=False, default=pyotp.random_base32()
    )
    setting_up_two_factor_authentication = Column(Boolean, nullable=False, default=False)
    #servers = relationship("Server", back_populates="user")

    def to_dict(self):
            """
            Converts the User object to a dictionary.

            Returns:
                dict: A dictionary representation of the User object.
            """
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_two_factor_auth_setup_uri(self):
        """
        Generates the setup URI for two-factor authentication.
        Returns:
            str: The setup URI for two-factor authentication.
        """
        return pyotp.totp.TOTP(
            s=self.two_factor_authentication_secret,
            interval=config_data["2fa"]["period"],
            digits=config_data["2fa"]["digits"],
        ).provisioning_uri(
            name=str(self.uuid), issuer_name=config_data["2fa"]["issuer_name"]
        )
    
    def verify_two_factor_auth(self, user_otp:str):
            """
            Verifies the user's one-time password (OTP) for two-factor authentication.

            Args:
                user_otp (str): The one-time password entered by the user.

            Returns:
                bool: True if the OTP is valid, False otherwise.
            """
            totp = pyotp.parse_uri(self.get_two_factor_auth_setup_uri())
            return totp.verify(user_otp)
