"""
Application configuration module.
Loads and validates configuration from environment variables.
"""

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DB_URL (str): Database connection URL.
        JWT_SECRET (str): Secret key for JWT token generation.
        JWT_ALGORITHM (str): Algorithm used for JWT token generation. Defaults to "HS256".
        JWT_EXPIRATION_SECONDS (int): Token expiration time in seconds. Defaults to 3600.

        MAIL_USERNAME (EmailStr): Email username for SMTP server.
        MAIL_PASSWORD (str): Email password for SMTP server.
        MAIL_FROM (EmailStr): Sender email address.
        MAIL_PORT (int): SMTP server port. Defaults to 465.
        MAIL_SERVER (str): SMTP server hostname.
        MAIL_FROM_NAME (str): Sender name for emails.
        MAIL_STARTTLS (bool): Whether to use STARTTLS. Defaults to False.
        MAIL_SSL_TLS (bool): Whether to use SSL/TLS. Defaults to True.
        USE_CREDENTIALS (bool): Whether to use SMTP authentication. Defaults to True.
        VALIDATE_CERTS (bool): Whether to validate SSL certificates. Defaults to True.

        CLD_NAME (str): Cloudinary cloud name.
        CLD_API_KEY (int): Cloudinary API key.
        CLD_API_SECRET (str): Cloudinary API secret.

        REDIS_HOST (str): Redis server hostname. Defaults to "localhost".
        REDIS_PORT (int): Redis server port. Defaults to 6379.
        REDIS_PASSWORD (str | None): Redis password. Defaults to None.
        REDIS_DB (int): Redis database number. Defaults to 0.
        REDIS_EXPIRE (int): Default cache expiration time in seconds. Defaults to 1800.
    """

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_EXPIRE: int = 1800  # 30 minutes default cache expiration

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
