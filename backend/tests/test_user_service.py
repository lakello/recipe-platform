import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.user import UserService


def make_user(**kwargs) -> User:
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": "hashed",
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


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def service(mock_repo: AsyncMock) -> UserService:
    return UserService(mock_repo)


async def test_create_user_success(service: UserService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_email.return_value = None
    mock_repo.get_by_username.return_value = None
    mock_repo.create.return_value = make_user()

    data = UserCreate(
        email="test@example.com", username="testuser", password="password123"
    )
    result = await service.create_user(data)

    assert result.email == "test@example.com"
    assert result.username == "testuser"
    mock_repo.create.assert_called_once()


async def test_create_user_duplicate_email(
    service: UserService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = make_user()

    data = UserCreate(
        email="existing@example.com", username="newuser", password="password123"
    )
    with pytest.raises(HTTPException) as exc:
        await service.create_user(data)

    assert exc.value.status_code == 409
    mock_repo.create.assert_not_called()


async def test_create_user_duplicate_username(
    service: UserService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = None
    mock_repo.get_by_username.return_value = make_user()

    data = UserCreate(
        email="new@example.com", username="existing", password="password123"
    )
    with pytest.raises(HTTPException) as exc:
        await service.create_user(data)

    assert exc.value.status_code == 409
    mock_repo.create.assert_not_called()


async def test_get_by_id_found(service: UserService, mock_repo: AsyncMock) -> None:
    user_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = make_user(id=user_id)

    result = await service.get_by_id(user_id)

    assert result is not None
    assert result.id == user_id


async def test_get_by_id_not_found(service: UserService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_id.return_value = None

    result = await service.get_by_id(uuid.uuid4())

    assert result is None


async def test_get_by_email_found(service: UserService, mock_repo: AsyncMock) -> None:
    mock_repo.get_by_email.return_value = make_user(email="found@example.com")

    result = await service.get_by_email("found@example.com")

    assert result is not None
    assert result.email == "found@example.com"


async def test_get_by_email_not_found(
    service: UserService, mock_repo: AsyncMock
) -> None:
    mock_repo.get_by_email.return_value = None

    result = await service.get_by_email("notfound@example.com")

    assert result is None
