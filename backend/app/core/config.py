from pydantic import field_validator
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
    s3_secret_key: str = "minioadmin"
    s3_bucket_photos: str = "recipe-photos"
    s3_bucket_avatars: str = "avatars"

    jwt_secret: str = "change-me-in-production"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    opensearch_url: str = "http://localhost:9200"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


settings = Settings()
