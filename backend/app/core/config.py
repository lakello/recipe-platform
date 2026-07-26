from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "local"
    app_name: str = "recipe-platform-backend"

    database_url: str = "postgresql+psycopg://recipe:recipe@localhost:5432/recipe"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend_url: str = "redis://localhost:6379/2"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_public_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = Field(default="minioadmin", repr=False)
    s3_bucket_photos: str = "recipe-photos"
    s3_bucket_avatars: str = "avatars"
    upload_max_bytes: int = 10 * 1024 * 1024
    upload_max_pixels: int = 40_000_000
    upload_intent_ttl_minutes: int = 15

    jwt_secret: str = Field(default="change-me-in-production", repr=False)
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    opensearch_url: str = "http://localhost:9200"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    google_client_id: str = ""
    google_client_secret: str = Field(default="", repr=False)
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    yandex_client_id: str = ""
    yandex_client_secret: str = Field(default="", repr=False)
    yandex_redirect_uri: str = "http://localhost:8000/api/auth/yandex/callback"

    frontend_url: str = "http://localhost:5173"

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_from: str = "noreply@recipe-platform.local"
    smtp_user: str = ""
    smtp_password: str = Field(default="", repr=False)
    smtp_tls: bool = False
    email_notifications_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @model_validator(mode="after")
    def validate_runtime_security(self) -> "Settings":
        if self.app_env.lower() in {"local", "test"}:
            return self

        errors = []
        if len(self.jwt_secret) < 32 or self.jwt_secret.lower() in {
            "change-me",
            "change-me-in-production",
            "secret",
            "test",
        }:
            errors.append("JWT_SECRET must be at least 32 characters and non-default")

        required = {
            "DATABASE_URL": self.database_url,
            "REDIS_URL": self.redis_url,
            "S3_ENDPOINT_URL": self.s3_endpoint_url,
            "S3_PUBLIC_URL": self.s3_public_url,
            "S3_ACCESS_KEY": self.s3_access_key,
            "S3_SECRET_KEY": self.s3_secret_key,
            "S3_BUCKET_PHOTOS": self.s3_bucket_photos,
            "S3_BUCKET_AVATARS": self.s3_bucket_avatars,
            "GOOGLE_CLIENT_ID": self.google_client_id,
            "GOOGLE_CLIENT_SECRET": self.google_client_secret,
            "GOOGLE_REDIRECT_URI": self.google_redirect_uri,
            "YANDEX_CLIENT_ID": self.yandex_client_id,
            "YANDEX_CLIENT_SECRET": self.yandex_client_secret,
            "YANDEX_REDIRECT_URI": self.yandex_redirect_uri,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if missing:
            errors.append(f"required settings are missing: {', '.join(missing)}")

        unsafe_markers = {
            "localhost",
            "127.0.0.1",
            "recipe_pass",
            "redis_pass",
            "minioadmin",
            "minio_secure_password",
            "idexample",
            "secretexample",
        }
        unsafe = [
            name
            for name, value in required.items()
            if any(marker in value.lower() for marker in unsafe_markers)
        ]
        if unsafe:
            errors.append(f"local or example values are forbidden: {', '.join(unsafe)}")

        if self.app_env.lower() == "production" and not self.cookie_secure:
            errors.append("COOKIE_SECURE must be enabled in production")

        if errors:
            raise ValueError("; ".join(errors))
        return self


settings = Settings()
