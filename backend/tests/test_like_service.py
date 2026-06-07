import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.like import Favorite, Like
from app.models.recipe import Recipe, RecipeStatus, RecipeVisibility
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.recipe import RecipeRepository
from app.services.like import FavoriteService, LikeService


def make_recipe(**kwargs) -> Recipe:
    author_id = kwargs.pop("author_id", uuid.uuid4())
    defaults = {
        "id": uuid.uuid4(),
        "author_id": author_id,
        "title": "Test Recipe",
        "description": None,
        "status": RecipeStatus.published,
        "visibility": RecipeVisibility.public,
        "cooking_time_minutes": None,
        "servings": None,
        "difficulty": None,
        "category_id": None,
        "category": None,
        "photo": None,
        "ingredients": [],
        "steps": [],
        "likes_count": 0,
        "is_liked": False,
        "is_favorited": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    recipe = MagicMock(spec=Recipe)
    for key, value in defaults.items():
        setattr(recipe, key, value)
    return recipe


def make_like(user_id: uuid.UUID, recipe_id: uuid.UUID) -> Like:
    like = MagicMock(spec=Like)
    like.id = uuid.uuid4()
    like.user_id = user_id
    like.recipe_id = recipe_id
    return like


def make_favorite(user_id: uuid.UUID, recipe_id: uuid.UUID) -> Favorite:
    fav = MagicMock(spec=Favorite)
    fav.id = uuid.uuid4()
    fav.user_id = user_id
    fav.recipe_id = recipe_id
    return fav


@pytest.fixture
def like_repo() -> AsyncMock:
    return AsyncMock(spec=LikeRepository)


@pytest.fixture
def favorite_repo() -> AsyncMock:
    return AsyncMock(spec=FavoriteRepository)


@pytest.fixture
def recipe_repo() -> AsyncMock:
    return AsyncMock(spec=RecipeRepository)


@pytest.fixture
def like_service(like_repo: AsyncMock, recipe_repo: AsyncMock) -> LikeService:
    return LikeService(like_repo, recipe_repo)


@pytest.fixture
def favorite_service(
    favorite_repo: AsyncMock, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> FavoriteService:
    return FavoriteService(favorite_repo, like_repo, recipe_repo)


# --- LikeService tests ---


async def test_like_recipe_success(
    like_service: LikeService, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    like_repo.get.return_value = None
    like_repo.count.return_value = 1

    result = await like_service.like(recipe.id, uuid.uuid4())

    assert result.likes_count == 1
    assert result.is_liked is True
    like_repo.add.assert_called_once()


async def test_like_recipe_already_liked(
    like_service: LikeService, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> None:
    recipe = make_recipe()
    user_id = uuid.uuid4()
    recipe_repo.get_by_id.return_value = recipe
    like_repo.get.return_value = make_like(user_id, recipe.id)

    with pytest.raises(HTTPException) as exc:
        await like_service.like(recipe.id, user_id)

    assert exc.value.status_code == 409


async def test_like_recipe_not_found(
    like_service: LikeService, recipe_repo: AsyncMock
) -> None:
    recipe_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await like_service.like(uuid.uuid4(), uuid.uuid4())

    assert exc.value.status_code == 404


async def test_unlike_recipe_success(
    like_service: LikeService, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> None:
    recipe = make_recipe()
    user_id = uuid.uuid4()
    existing_like = make_like(user_id, recipe.id)
    recipe_repo.get_by_id.return_value = recipe
    like_repo.get.return_value = existing_like
    like_repo.count.return_value = 0

    result = await like_service.unlike(recipe.id, user_id)

    assert result.likes_count == 0
    assert result.is_liked is False
    like_repo.remove.assert_called_once_with(existing_like)


async def test_unlike_recipe_not_liked(
    like_service: LikeService, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    like_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await like_service.unlike(recipe.id, uuid.uuid4())

    assert exc.value.status_code == 404


async def test_get_like_status_authenticated(
    like_service: LikeService, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> None:
    recipe = make_recipe()
    user_id = uuid.uuid4()
    recipe_repo.get_by_id.return_value = recipe
    like_repo.count.return_value = 5
    like_repo.get.return_value = make_like(user_id, recipe.id)

    result = await like_service.get_status(recipe.id, user_id)

    assert result.likes_count == 5
    assert result.is_liked is True


async def test_get_like_status_unauthenticated(
    like_service: LikeService, like_repo: AsyncMock, recipe_repo: AsyncMock
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    like_repo.count.return_value = 3

    result = await like_service.get_status(recipe.id, None)

    assert result.likes_count == 3
    assert result.is_liked is False
    like_repo.get.assert_not_called()


# --- FavoriteService tests ---


async def test_add_favorite_success(
    favorite_service: FavoriteService,
    favorite_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    favorite_repo.get.return_value = None

    result = await favorite_service.add_favorite(recipe.id, uuid.uuid4())

    assert result.is_favorited is True
    favorite_repo.add.assert_called_once()


async def test_add_favorite_already_favorited(
    favorite_service: FavoriteService,
    favorite_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    user_id = uuid.uuid4()
    recipe_repo.get_by_id.return_value = recipe
    favorite_repo.get.return_value = make_favorite(user_id, recipe.id)

    with pytest.raises(HTTPException) as exc:
        await favorite_service.add_favorite(recipe.id, user_id)

    assert exc.value.status_code == 409


async def test_remove_favorite_success(
    favorite_service: FavoriteService,
    favorite_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    user_id = uuid.uuid4()
    existing = make_favorite(user_id, recipe.id)
    recipe_repo.get_by_id.return_value = recipe
    favorite_repo.get.return_value = existing

    result = await favorite_service.remove_favorite(recipe.id, user_id)

    assert result.is_favorited is False
    favorite_repo.remove.assert_called_once_with(existing)


async def test_remove_favorite_not_found(
    favorite_service: FavoriteService,
    favorite_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    favorite_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await favorite_service.remove_favorite(recipe.id, uuid.uuid4())

    assert exc.value.status_code == 404


async def test_list_favorites_empty(
    favorite_service: FavoriteService,
    favorite_repo: AsyncMock,
) -> None:
    favorite_repo.list_by_user.return_value = []

    result = await favorite_service.list_favorites(uuid.uuid4())

    assert result == []


async def test_list_favorites_returns_recipes(
    favorite_service: FavoriteService,
    favorite_repo: AsyncMock,
    like_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    user_id = uuid.uuid4()
    recipe = make_recipe()
    favorite_repo.list_by_user.return_value = [recipe.id]
    like_repo.count_batch.return_value = {recipe.id: 2}
    like_repo.user_liked_batch.return_value = {recipe.id}
    recipe_repo.get_by_id.return_value = recipe

    result = await favorite_service.list_favorites(user_id)

    assert len(result) == 1
    assert result[0].likes_count == 2
    assert result[0].is_liked is True
    assert result[0].is_favorited is True
