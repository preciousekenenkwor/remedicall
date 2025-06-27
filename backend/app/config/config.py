from enum import Enum
from typing import TypedDict

from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenType(Enum):
    VERIFY_EMAIL ="VERIFY_EMAIL"
    RESET_PASSWORD="RESET_PASSWORD"
    REFRESH_TOKEN="REFRESH_TOKEN"
    ACCESS_TOKEN="ACCESS_TOKEN"

    # convert enum to string
    def __str__(self)->str:
        return self.value
    
    
    
    






class Mail_Env_Type(TypedDict):
    mail_server: str
    mail_port: int
    mail_username: str
    mail_password: str
    use_credentials: bool
    mail_use_ssl: bool
    mail_use_tls: bool
    mail_sender: str
    mail_sender_name: str
    use_mail_service: bool


class Social_Env_Type(TypedDict):
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    facebook_client_id: str
    facebook_client_secret: str
    facebook_redirect_uri: str
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str


class JWT_Env_Type(TypedDict):
    jwt_secret: str
    jwt_access_expiry_time: int
    jwt_refresh_expiry_time: int
    jwt_expiry_time: str


class env_type(TypedDict):
    jwt: JWT_Env_Type
    env_type: str

    database_url: str
    mail: Mail_Env_Type
    social: Social_Env_Type


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", validate_default=False
    )
    jwt_secret: str = ""
    jwt_access_expiry_time: str = ""
    jwt_refresh_expiry_time: str = ""
    jwt_expiry_time: str = ""
    database_url: str = ""
    mail_server: str = ""
    mail_port: int = 0
    mail_username: str = ""
    mail_password: str = ""
    use_credentials: bool = False
    mail_use_ssl: bool = False
    mail_use_tls: bool = False
    mail_sender: str = ""
    mail_sender_name: str = ""
    env_type: str = ""
    use_mail_service: bool = False

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    facebook_client_id: str = ""
    facebook_client_secret: str = ""
    facebook_redirect_uri: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = ""


# @lru_cache
settings: Settings = Settings()

env: env_type = {
    "database_url": settings.database_url,
    "env_type": settings.env_type,
    "jwt": {
        "jwt_expiry_time": settings.jwt_expiry_time,
        "jwt_secret": settings.jwt_secret,
        "jwt_access_expiry_time": int(settings.jwt_access_expiry_time),
        "jwt_refresh_expiry_time": int(settings.jwt_refresh_expiry_time),
    },
    "mail": {
        "mail_password": settings.mail_password,
        "mail_port": settings.mail_port,
        "mail_server": settings.mail_server,
        "mail_sender": settings.mail_sender,
        "mail_use_tls": settings.mail_use_tls,
        "mail_use_ssl": settings.mail_use_ssl,
        "mail_username": settings.mail_username,
        "use_credentials": settings.use_credentials,
        "mail_sender_name": settings.mail_sender_name,
        "use_mail_service": settings.use_mail_service,
    },
    "social": {
        "google_client_id": settings.google_client_id,
        "google_client_secret": settings.google_client_secret,
        "google_redirect_uri": settings.google_redirect_uri,
        "facebook_client_id": settings.facebook_client_id,
        "facebook_client_secret": settings.facebook_client_secret,
        "facebook_redirect_uri": settings.facebook_redirect_uri,
        "github_client_id": settings.github_client_id,
        "github_client_secret": settings.github_client_secret,
        "github_redirect_uri": settings.github_redirect_uri,
    },
}
