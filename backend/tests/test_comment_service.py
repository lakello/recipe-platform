import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.comment import Comment
from app.models.recipe import Recipe, RecipeStatus, RecipeVisibility
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.comment import CommentService


def make_user(username: str = "tester") -> User:
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.username = username
    user.avatar_url = None
    user.role = "user"
    return user


def make_recipe(**kwargs) -> Recipe:
    recipe = MagicMock(spec=Recipe)
    recipe.id = uuid.uuid4()
    recipe.status = RecipeStatus.published
    recipe.visibility = RecipeVisibility.public
    for k, v in kwargs.items():
        setattr(recipe, k, v)
    return recipe


def make_comment(**kwargs) -> Comment:
    author = kwargs.pop("author", make_user())
    defaults = {
        "id": uuid.uuid4(),
        "recipe_id": uuid.uuid4(),
        "author_id": author.id,
        "parent_id": None,
        "body": "Test comment",
        "is_hidden": False,
        "is_deleted": False,
        "author": author,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    comment = MagicMock(spec=Comment)
    for key, value in defaults.items():
        setattr(comment, key, value)
    return comment


@pytest.fixture
def comment_repo() -> AsyncMock:
    return AsyncMock(spec=CommentRepository)


@pytest.fixture
def recipe_repo() -> AsyncMock:
    return AsyncMock(spec=RecipeRepository)


@pytest.fixture
def service(comment_repo: AsyncMock, recipe_repo: AsyncMock) -> CommentService:
    return CommentService(comment_repo, recipe_repo)


# --- add_comment ---


async def test_add_comment_success(
    service: CommentService,
    comment_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    comment = make_comment(recipe_id=recipe.id, body="Отличный рецепт!")
    comment_repo.create.return_value = comment

    data = CommentCreate(body="Отличный рецепт!")
    result = await service.add_comment(recipe.id, comment.author_id, data)

    assert result.body == "Отличный рецепт!"
    comment_repo.create.assert_called_once()


async def test_add_comment_recipe_not_found(
    service: CommentService,
    recipe_repo: AsyncMock,
) -> None:
    recipe_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.add_comment(uuid.uuid4(), uuid.uuid4(), CommentCreate(body="Hi"))
    assert exc.value.status_code == 404


async def test_add_reply_success(
    service: CommentService,
    comment_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    parent = make_comment(recipe_id=recipe.id, parent_id=None)
    reply = make_comment(recipe_id=recipe.id, parent_id=parent.id)
    comment_repo.get_by_id.return_value = parent
    comment_repo.create.return_value = reply

    data = CommentCreate(body="Ответ", parent_id=parent.id)
    result = await service.add_comment(recipe.id, reply.author_id, data)

    assert result.parent_id == parent.id


async def test_add_reply_to_reply_rejected(
    service: CommentService,
    comment_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe
    nested = make_comment(recipe_id=recipe.id, parent_id=uuid.uuid4())
    comment_repo.get_by_id.return_value = nested

    with pytest.raises(HTTPException) as exc:
        await service.add_comment(
            recipe.id, uuid.uuid4(), CommentCreate(body="Hi", parent_id=nested.id)
        )
    assert exc.value.status_code == 400


# --- edit_comment ---


async def test_edit_comment_success(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    author_id = uuid.uuid4()
    comment = make_comment(author_id=author_id)
    updated = make_comment(author_id=author_id, body="Изменено")
    comment_repo.get_by_id.return_value = comment
    comment_repo.update.return_value = updated

    result = await service.edit_comment(
        comment.id, author_id, CommentUpdate(body="Изменено")
    )
    assert result.body == "Изменено"


async def test_edit_comment_wrong_author(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    comment = make_comment()
    comment_repo.get_by_id.return_value = comment

    with pytest.raises(HTTPException) as exc:
        await service.edit_comment(
            comment.id, uuid.uuid4(), CommentUpdate(body="Hacked")
        )
    assert exc.value.status_code == 403


async def test_edit_deleted_comment_rejected(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    author_id = uuid.uuid4()
    comment = make_comment(author_id=author_id, is_deleted=True)
    comment_repo.get_by_id.return_value = comment

    with pytest.raises(HTTPException) as exc:
        await service.edit_comment(
            comment.id, author_id, CommentUpdate(body="Try edit")
        )
    assert exc.value.status_code == 404


# --- delete_comment ---


async def test_delete_comment_success(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    author_id = uuid.uuid4()
    comment = make_comment(author_id=author_id)
    comment_repo.get_by_id.return_value = comment

    await service.delete_comment(comment.id, author_id)
    comment_repo.update.assert_called_once_with(comment, {"is_deleted": True})


async def test_delete_comment_wrong_author(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    comment = make_comment()
    comment_repo.get_by_id.return_value = comment

    with pytest.raises(HTTPException) as exc:
        await service.delete_comment(comment.id, uuid.uuid4())
    assert exc.value.status_code == 403


# --- hide / unhide ---


async def test_hide_comment(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    comment = make_comment()
    hidden = make_comment(
        author_id=comment.author_id,
        author=comment.author,
        is_hidden=True,
    )
    comment_repo.get_by_id.return_value = comment
    comment_repo.update.return_value = hidden

    result = await service.hide_comment(comment.id)
    assert result.is_hidden is True


async def test_unhide_comment(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    comment = make_comment(is_hidden=True)
    visible = make_comment(
        author_id=comment.author_id,
        author=comment.author,
        is_hidden=False,
    )
    comment_repo.get_by_id.return_value = comment
    comment_repo.update.return_value = visible

    result = await service.unhide_comment(comment.id)
    assert result.is_hidden is False


# --- body masking ---


async def test_deleted_comment_body_masked(
    service: CommentService,
    comment_repo: AsyncMock,
) -> None:
    author_id = uuid.uuid4()
    original = make_comment(author_id=author_id, is_deleted=False)
    deleted = make_comment(
        author_id=author_id,
        author=original.author,
        is_deleted=True,
        body="secret",
    )
    comment_repo.get_by_id.return_value = original
    comment_repo.update.return_value = deleted

    await service.delete_comment(original.id, author_id)
    result = CommentUpdate(body="irrelevant")
    _ = result  # just checking delete works; schema masking tested separately


async def test_comment_read_masks_hidden_body() -> None:
    from app.schemas.comment import CommentAuthor, CommentRead

    author = CommentAuthor(
        id=uuid.uuid4(), username="user", avatar_url=None, role="user"
    )
    comment = CommentRead(
        id=uuid.uuid4(),
        recipe_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        parent_id=None,
        body="Original text",
        is_hidden=True,
        is_deleted=False,
        author=author,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert comment.body == "Комментарий скрыт модератором"


async def test_comment_read_masks_deleted_body() -> None:
    from app.schemas.comment import CommentAuthor, CommentRead

    author = CommentAuthor(
        id=uuid.uuid4(), username="user", avatar_url=None, role="user"
    )
    comment = CommentRead(
        id=uuid.uuid4(),
        recipe_id=uuid.uuid4(),
        author_id=uuid.uuid4(),
        parent_id=None,
        body="Original text",
        is_hidden=False,
        is_deleted=True,
        author=author,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert comment.body == "Комментарий удалён"
