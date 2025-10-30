from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARN", "ERROR"]

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str

    OAUTH_GOOGLE_CLIENT_ID: str
    OAUTH_GOOGLE_CLIENT_SECRET: str
    OAUTH_GOOGLE_BASE_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    OAUTH_GOOGLE_REDIRECT_URL: str
    FRONTEND_URL: str

    GOOGLE_JWKS_URL: str = "https://www.googleapis.com/oauth2/v3/certs"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"

    SIZE_POOL_AIOHTTP: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str
    SMTP_TIMEOUT: float

    USER_VERIFY_RATE_LIMIT: int = 60
    USER_VERIFICATION_CODE_EXP: int = 600
    PASSWORD_RESET_CODE_EXP: int = 600

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://default:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=[".env-example", ".env"], extra="ignore")


settings = Settings()
