from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    allowed_origins: str = "http://localhost:4321"

    admin_nombre: str
    admin_correo: str
    admin_documento: str
    admin_password: str

    environment: str = "development"

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "t", "yes", "y", "on", "debug", "development", "dev"}:
                return True
            if normalized in {"0", "false", "f", "no", "n", "off", "release", "production", "prod"}:
                return False
        return value

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
