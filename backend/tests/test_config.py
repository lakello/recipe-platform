import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_local_config_uses_development_defaults() -> None:
    settings = Settings(_env_file=None, app_env="local")

    assert settings.cookie_secure is False
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_production_rejects_insecure_defaults() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET.*COOKIE_SECURE"):
        Settings(_env_file=None, app_env="production")
