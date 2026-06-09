import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.moderation_action import ModerationAction
from app.models.report import Report, ReportReason, ReportStatus, ReportTargetType
from app.models.user import User, UserRole
from app.repositories.comment import CommentRepository
from app.repositories.moderation_action import ModerationActionRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.report import ReportRepository
from app.repositories.user import UserRepository
from app.schemas.admin import ReportCreate
from app.services.admin import AdminService


def make_user(**kwargs) -> User:
    defaults = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": "hashed",  # pragma: allowlist secret
        "is_email_verified": True,
        "is_active": True,
        "role": UserRole.user,
        "avatar_url": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    user = MagicMock(spec=User)
    for key, value in defaults.items():
        setattr(user, key, value)
    return user


def make_report(**kwargs) -> Report:
    defaults = {
        "id": uuid.uuid4(),
        "reporter_id": uuid.uuid4(),
        "target_type": ReportTargetType.recipe,
        "target_id": uuid.uuid4(),
        "reason": ReportReason.spam,
        "description": None,
        "status": ReportStatus.pending,
        "reviewed_by": None,
        "reviewed_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    report = MagicMock(spec=Report)
    for key, value in defaults.items():
        setattr(report, key, value)
    return report


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_recipe_repo() -> AsyncMock:
    return AsyncMock(spec=RecipeRepository)


@pytest.fixture
def mock_comment_repo() -> AsyncMock:
    return AsyncMock(spec=CommentRepository)


@pytest.fixture
def mock_report_repo() -> AsyncMock:
    return AsyncMock(spec=ReportRepository)


@pytest.fixture
def mock_audit_repo() -> AsyncMock:
    return AsyncMock(spec=ModerationActionRepository)


@pytest.fixture
def service(
    mock_user_repo: AsyncMock,
    mock_recipe_repo: AsyncMock,
    mock_comment_repo: AsyncMock,
    mock_report_repo: AsyncMock,
    mock_audit_repo: AsyncMock,
) -> AdminService:
    return AdminService(
        mock_user_repo,
        mock_recipe_repo,
        mock_comment_repo,
        mock_report_repo,
        mock_audit_repo,
    )


# ── assign role ──────────────────────────────────────────────────────────────


async def test_assign_role_success(
    service: AdminService,
    mock_user_repo: AsyncMock,
    mock_audit_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.admin)
    target = make_user(id=uuid.uuid4(), role=UserRole.user)
    mock_user_repo.get_by_id.return_value = target
    mock_user_repo.update.return_value = make_user(
        id=target.id, role=UserRole.moderator
    )
    mock_audit_repo.create.return_value = MagicMock(spec=ModerationAction)

    result = await service.assign_role(target.id, UserRole.moderator, actor)

    assert result is not None
    mock_user_repo.update.assert_called_once()


async def test_assign_role_cannot_change_own(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    actor_id = uuid.uuid4()
    actor = make_user(id=actor_id, role=UserRole.admin)
    target = make_user(id=actor_id, role=UserRole.admin)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(actor_id, UserRole.user, actor)
    assert exc.value.status_code == 400


async def test_assign_superadmin_always_forbidden(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    """Superadmin role cannot be assigned via panel by anyone."""
    actor = make_user(role=UserRole.superadmin)
    target = make_user(id=uuid.uuid4(), role=UserRole.user)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(target.id, UserRole.superadmin, actor)
    assert exc.value.status_code == 403


async def test_assign_role_admin_cannot_touch_admin(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.admin)
    target = make_user(id=uuid.uuid4(), role=UserRole.admin)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(target.id, UserRole.user, actor)
    assert exc.value.status_code == 403


async def test_assign_role_superadmin_target_untouchable(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.admin)
    target = make_user(id=uuid.uuid4(), role=UserRole.superadmin)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.assign_role(target.id, UserRole.user, actor)
    assert exc.value.status_code == 403


# ── block / unblock ───────────────────────────────────────────────────────────


async def test_block_user_success(
    service: AdminService,
    mock_user_repo: AsyncMock,
    mock_audit_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.superadmin)
    target = make_user(id=uuid.uuid4(), is_active=True, role=UserRole.user)
    mock_user_repo.get_by_id.return_value = target
    mock_user_repo.update.return_value = make_user(id=target.id, is_active=False)
    mock_audit_repo.create.return_value = MagicMock(spec=ModerationAction)

    result = await service.block_user(target.id, actor, "spam")

    assert result is not None
    mock_user_repo.update.assert_called_once()


async def test_block_already_blocked(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.superadmin)
    target = make_user(id=uuid.uuid4(), is_active=False, role=UserRole.user)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.block_user(target.id, actor, None)
    assert exc.value.status_code == 409


async def test_block_self_forbidden(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    actor_id = uuid.uuid4()
    actor = make_user(id=actor_id, role=UserRole.superadmin)
    target = make_user(id=actor_id, is_active=True, role=UserRole.superadmin)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.block_user(actor_id, actor, None)
    assert exc.value.status_code == 400


async def test_block_superadmin_forbidden(
    service: AdminService,
    mock_user_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.superadmin)
    target = make_user(id=uuid.uuid4(), is_active=True, role=UserRole.superadmin)
    mock_user_repo.get_by_id.return_value = target

    with pytest.raises(HTTPException) as exc:
        await service.block_user(target.id, actor, None)
    assert exc.value.status_code == 403


async def test_unblock_user_success(
    service: AdminService,
    mock_user_repo: AsyncMock,
    mock_audit_repo: AsyncMock,
) -> None:
    actor = make_user(role=UserRole.admin)
    target = make_user(id=uuid.uuid4(), is_active=False)
    mock_user_repo.get_by_id.return_value = target
    mock_user_repo.update.return_value = make_user(id=target.id, is_active=True)
    mock_audit_repo.create.return_value = MagicMock(spec=ModerationAction)

    result = await service.unblock_user(target.id, actor)

    assert result is not None
    mock_user_repo.update.assert_called_once()


# ── reports ───────────────────────────────────────────────────────────────────


async def test_create_report(
    service: AdminService,
    mock_report_repo: AsyncMock,
) -> None:
    reporter_id = uuid.uuid4()
    target_id = uuid.uuid4()
    mock_report_repo.create.return_value = make_report(
        reporter_id=reporter_id, target_id=target_id
    )

    data = ReportCreate(
        target_type=ReportTargetType.recipe,
        target_id=target_id,
        reason=ReportReason.spam,
    )
    result = await service.create_report(data, reporter_id)

    assert result is not None
    mock_report_repo.create.assert_called_once()


async def test_review_report_success(
    service: AdminService,
    mock_report_repo: AsyncMock,
    mock_audit_repo: AsyncMock,
) -> None:
    reviewer = make_user(role=UserRole.moderator)
    report = make_report(status=ReportStatus.pending)
    mock_report_repo.get_by_id.return_value = report
    mock_report_repo.update.return_value = make_report(
        id=report.id, status=ReportStatus.reviewed
    )
    mock_audit_repo.create.return_value = MagicMock(spec=ModerationAction)

    result = await service.review_report(report.id, reviewer)

    assert result is not None


async def test_review_already_processed_report(
    service: AdminService,
    mock_report_repo: AsyncMock,
) -> None:
    reviewer = make_user(role=UserRole.moderator)
    report = make_report(status=ReportStatus.reviewed)
    mock_report_repo.get_by_id.return_value = report

    with pytest.raises(HTTPException) as exc:
        await service.review_report(report.id, reviewer)
    assert exc.value.status_code == 409


# ── recipe hide/unhide ────────────────────────────────────────────────────────


async def test_hide_recipe_success(
    service: AdminService,
    mock_recipe_repo: AsyncMock,
    mock_audit_repo: AsyncMock,
) -> None:
    from app.models.recipe import Recipe

    actor = make_user(role=UserRole.moderator)
    author = make_user(id=uuid.uuid4(), role=UserRole.user)

    def make_recipe_mock(is_hidden: bool) -> MagicMock:
        r = MagicMock(spec=Recipe)
        r.id = uuid.uuid4()
        r.is_hidden = is_hidden
        r.title = "Test"
        r.author_id = author.id
        r.author = author
        r.status = "published"
        r.visibility = "public"
        r.created_at = datetime.now(UTC)
        return r

    recipe = make_recipe_mock(False)
    mock_recipe_repo.get_by_id.return_value = recipe
    hidden_recipe = make_recipe_mock(True)
    hidden_recipe.id = recipe.id
    mock_recipe_repo.update.return_value = hidden_recipe
    mock_audit_repo.create.return_value = MagicMock(spec=ModerationAction)

    result = await service.hide_recipe(recipe.id, actor, "spam")

    assert result.is_hidden is True


async def test_hide_already_hidden_recipe(
    service: AdminService,
    mock_recipe_repo: AsyncMock,
) -> None:
    from app.models.recipe import Recipe

    actor = make_user(role=UserRole.moderator)
    recipe = MagicMock(spec=Recipe)
    recipe.id = uuid.uuid4()
    recipe.is_hidden = True
    recipe.author = make_user()
    mock_recipe_repo.get_by_id.return_value = recipe

    with pytest.raises(HTTPException) as exc:
        await service.hide_recipe(recipe.id, actor, None)
    assert exc.value.status_code == 409
