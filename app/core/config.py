from pydantic_settings import BaseSettings

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

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
