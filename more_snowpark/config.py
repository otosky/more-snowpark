from importlib import import_module

try:
    import_module("pydantic")
    import_module("pydantic_settings")
except ImportError as e:
    raise ImportError("pydantic dependencies missing")

from pathlib import Path
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    snowflake_account: str
    snowflake_user: str
    snowflake_warehouse: str
    snowflake_database: str
    snowflake_schema: str
    snowflake_role: str
    snowflake_auth_strategy: str
    snowflake_password: Optional[SecretStr] = None
    snowflake_private_key_path: Optional[str] = None
    snowflake_private_key_password: Optional[SecretStr] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_private_key(self):
        private_key_path = Path(self.snowflake_private_key_path)
        if self.snowflake_private_key_password:
            private_key_password = self.snowflake_private_key_password.get_secret_value().encode()
        else:
            private_key_password = None

        rsa_key = serialization.load_pem_private_key(
            private_key_path.read_bytes(),
            password=private_key_password,
            backend=default_backend(),
        )

        return rsa_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    @property
    def auth_config(self) -> dict[str, str]:
        if self.snowflake_auth_strategy == "privatekey":
            auth_config = {"private_key": self.get_private_key()}
        elif self.snowflake_auth_strategy == "password":
            auth_config = {"password": self.snowpark_password.get_secret_value()}
        else:
            auth_config = {"authenticator": "externalbrowser"}

        return auth_config

    @property
    def snowflake_config(self) -> dict[str, str]:
        return {
            "account": self.snowflake_account,
            "user": self.snowflake_user,
            "warehouse": self.snowflake_warehouse,
            "database": self.snowflake_database,
            "schema": self.snowflake_schema,
            "role": self.snowflake_role,
            **self.auth_config,
        }
