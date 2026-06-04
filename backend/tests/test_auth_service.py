import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import bcrypt
import pytest
from fastapi import HTTPException

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth import AuthService


def make_user(**kwargs) -> User:
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": "",
        "is_email_verified": False,
        "is_active": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    user = MagicMock(spec=User)
    for key, value in defaults.items():
        setattr(user, key, value)
    return user


def make_refresh_token(
    user_id: uuid.UUID, token: str = "valid-token"
) -> RefreshToken:
    rt = MagicMock(spec=RefreshToken)
    rt.user_id = user_id
    rt.token = token
    rt.is_revoked = False
    rt.expires_at = datetime(2099, 1, 1, tzinfo=UTC)
    return rt


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def token_repo() -> AsyncMock:
    return AsyncMock(spec=RefreshTokenRepository)


@pytest.fixture
def service(user_repo: AsyncMock, token_repo: AsyncMock) -> AuthService:
    return AuthService(user_repo=user_repo, token_repo=token_repo)


async def test_register_success(
    service: AuthService, user_repo: AsyncMock, token_repo: AsyncMock
) -> None:
    user_repo.get_by_email.return_value = None
    user_repo.get_by_username.return_value = None
    user_repo.create.return_value = make_user()
    token_repo.create.return_value = MagicMock()

    data = RegisterRequest(
        email="test@example.com", username="testuser", password="password123"
    )
    result = await service.register(data)

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"


async def test_register_duplicate_email(
    service: AuthService, user_repo: AsyncMock
) -> None:
    user_repo.get_by_email.return_value = make_user()

    data = RegisterRequest(
        email="test@example.com", username="testuser", password="password123"
    )
    with pytest.raises(HTTPException) as exc:
        await service.register(data)

    assert exc.value.status_code == 409


async def test_register_duplicate_username(
    service: AuthService, user_repo: AsyncMock
) -> None:
    user_repo.get_by_email.return_value = None
    user_repo.get_by_username.return_value = make_user()

    data = RegisterRequest(
        email="new@example.com", username="testuser", password="password123"
    )
    with pytest.raises(HTTPException) as exc:
        await service.register(data)

    assert exc.value.status_code == 409


async def test_login_success(
    service: AuthService, user_repo: AsyncMock, token_repo: AsyncMock
) -> None:
    hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
    user_repo.get_by_email.return_value = make_user(password_hash=hashed)
    token_repo.create.return_value = MagicMock()

    data = LoginRequest(email="test@example.com", password="password123")
    result = await service.login(data)

    assert result.access_token
    assert result.refresh_token


async def test_login_wrong_password(
    service: AuthService, user_repo: AsyncMock
) -> None:
    hashed = bcrypt.hashpw(b"correctpassword", bcrypt.gensalt()).decode()
    user_repo.get_by_email.return_value = make_user(password_hash=hashed)

    data = LoginRequest(email="test@example.com", password="wrongpassword")
    with pytest.raises(HTTPException) as exc:
        await service.login(data)

    assert exc.value.status_code == 401


async def test_login_user_not_found(
    service: AuthService, user_repo: AsyncMock
) -> None:
    user_repo.get_by_email.return_value = None

    data = LoginRequest(email="nobody@example.com", password="password123")
    with pytest.raises(HTTPException) as exc:
        await service.login(data)

    assert exc.value.status_code == 401


async def test_refresh_success(
    service: AuthService, token_repo: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    token_repo.is_valid.return_value = True
    token_repo.get_by_token.return_value = make_refresh_token(user_id)
    token_repo.create.return_value = MagicMock()

    result = await service.refresh("valid-token")

    assert result.access_token
    token_repo.revoke.assert_called_once_with("valid-token")


async def test_refresh_invalid_token(
    service: AuthService, token_repo: AsyncMock
) -> None:
    token_repo.is_valid.return_value = False

    with pytest.raises(HTTPException) as exc:
        await service.refresh("bad-token")

    assert exc.value.status_code == 401


async def test_logout_success(
    service: AuthService, token_repo: AsyncMock
) -> None:
    await service.logout("some-token")
    token_repo.revoke.assert_called_once_with("some-token")
