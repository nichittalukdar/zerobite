from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ShareBite API"
    app_version: str = "1.0.0"
    developer_name: str = "Ripun"
    environment: str = "development"
    database_url: str = "sqlite:///./sharebite.db"
    jwt_secret_key: SecretStr = SecretStr(
        "replace-this-with-a-random-secret-at-least-32-characters-long"
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0, le=1440)
    cors_origins: str = "http://127.0.0.1:5500,http://localhost:5500"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_production_secrets(self):
        secret = self.jwt_secret_key.get_secret_value()
        if self.environment.lower() in {"production", "prod"}:
            if len(secret) < 32 or secret.startswith("replace-this"):
                raise ValueError("Set JWT_SECRET_KEY to a random secret of at least 32 characters in production.")
            if self.database_url.startswith("sqlite"):
                raise ValueError("Use PostgreSQL or another production database in production.")
        return self


settings = Settings()
