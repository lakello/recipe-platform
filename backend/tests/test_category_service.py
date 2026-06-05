import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import CategoryService


def make_category(**kwargs) -> Category:
    defaults = {
        "id": uuid.uuid4(),
        "name": "Супы",
        "slug": "supy",
        "description": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    category = MagicMock(spec=Category)
    for key, value in defaults.items():
        setattr(category, key, value)
    return category


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=CategoryRepository)


@pytest.fixture
def service(repo: AsyncMock) -> CategoryService:
    return CategoryService(repo)


async def test_list_categories(service: CategoryService, repo: AsyncMock) -> None:
    repo.list_all.return_value = [
        make_category(),
        make_category(name="Салаты", slug="salaty"),
    ]
    result = await service.list_categories()
    assert len(result) == 2


async def test_get_category(service: CategoryService, repo: AsyncMock) -> None:
    category = make_category()
    repo.get_by_id.return_value = category
    result = await service.get_category(category.id)
    assert result.id == category.id


async def test_get_category_not_found(
    service: CategoryService, repo: AsyncMock
) -> None:
    repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.get_category(uuid.uuid4())
    assert exc.value.status_code == 404


async def test_create_category(service: CategoryService, repo: AsyncMock) -> None:
    repo.get_by_slug.return_value = None
    repo.create.return_value = make_category(name="Супы", slug="supy")
    result = await service.create_category(CategoryCreate(name="Супы"))
    assert result.name == "Супы"
    assert result.slug == "supy"


async def test_create_category_duplicate(
    service: CategoryService, repo: AsyncMock
) -> None:
    repo.get_by_slug.return_value = make_category()
    with pytest.raises(HTTPException) as exc:
        await service.create_category(CategoryCreate(name="Супы"))
    assert exc.value.status_code == 409


async def test_update_category(service: CategoryService, repo: AsyncMock) -> None:
    category = make_category()
    updated = make_category(name="Закуски", slug="zakuski")
    repo.get_by_id.return_value = category
    repo.get_by_slug.return_value = None
    repo.update.return_value = updated
    result = await service.update_category(category.id, CategoryUpdate(name="Закуски"))
    assert result.name == "Закуски"


async def test_update_category_not_found(
    service: CategoryService, repo: AsyncMock
) -> None:
    repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.update_category(uuid.uuid4(), CategoryUpdate(name="X"))
    assert exc.value.status_code == 404


async def test_delete_category(service: CategoryService, repo: AsyncMock) -> None:
    category = make_category()
    repo.get_by_id.return_value = category
    await service.delete_category(category.id)
    repo.delete.assert_called_once_with(category)


async def test_delete_category_not_found(
    service: CategoryService, repo: AsyncMock
) -> None:
    repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await service.delete_category(uuid.uuid4())
    assert exc.value.status_code == 404
