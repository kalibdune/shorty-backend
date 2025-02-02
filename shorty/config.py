import os
import time

from pydantic import SecretStr
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict

os.environ["TZ"] = "UTC"
time.tzset()


class BaseConfig(_BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class PostgresConfig(BaseConfig, env_prefix="DB_"):
    host: str
    user: str
    password: SecretStr
    name: str
    port: int
    debug: bool

    @property
    def get_dsn(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class Config(BaseConfig):
    postgres: PostgresConfig


config = Config(postgres=PostgresConfig())
