import uuid
from datetime import UTC, datetime

from fastapi import HTTPException

from app.models.moderation_action import ActionType, ModerationAction
from app.models.report import Report, ReportStatus
from app.models.user import User, UserRole
from app.repositories.comment import CommentRepository
from app.repositories.moderation_action import ModerationActionRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.report import ReportRepository
from app.repositories.user import UserRepository
from app.schemas.admin import (
    AdminCommentPage,
    AdminCommentRead,
    AdminRecipePage,
    AdminRecipeRead,
    AdminUserPage,
    AdminUserRead,
    AuditPage,
    ModerationActionRead,
    ReportCreate,
    ReportPage,
    ReportRead,
)
from app.schemas.user import UserRead

_PAGE_MAX = 100


class AdminService:
    def __init__(
        self,
        user_repo: UserRepository,
        recipe_repo: RecipeRepository,
        comment_repo: CommentRepository,
        report_repo: ReportRepository,
        audit_repo: ModerationActionRepository,
    ) -> None:
        self.user_repo = user_repo
        self.recipe_repo = recipe_repo
        self.comment_repo = comment_repo
        self.report_repo = report_repo
        self.audit_repo = audit_repo

    # ── users ─────────────────────────────────────────────────────────────

    async def list_users(self, page: int, size: int) -> AdminUserPage:
        size = min(size, _PAGE_MAX)
        offset = (page - 1) * size
        users, total = await self.user_repo.list_all(offset, size)
        return AdminUserPage(
            items=[AdminUserRead.model_validate(u) for u in users],
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(users)) < total,
        )

    async def assign_role(
        self, user_id: uuid.UUID, role: UserRole, actor: User
    ) -> UserRead:
        user = await self._get_user(user_id)
        if user.id == actor.id:
            raise HTTPException(status_code=400, detail="Cannot change own role")
        if role == UserRole.superadmin and actor.role != UserRole.superadmin:
            raise HTTPException(
                status_code=403, detail="Only superadmin can assign superadmin role"
            )
        old_role = user.role
        user = await self.user_repo.update(user, {"role": role})
        await self._log(
            actor,
            ActionType.assign_role,
            "user",
            user_id,
            meta={"old_role": old_role, "new_role": role},
        )
        return UserRead.model_validate(user)

    async def block_user(
        self, user_id: uuid.UUID, actor: User, reason: str | None
    ) -> UserRead:
        user = await self._get_user(user_id)
        if user.id == actor.id:
            raise HTTPException(status_code=400, detail="Cannot block yourself")
        if not user.is_active:
            raise HTTPException(status_code=409, detail="User is already blocked")
        user = await self.user_repo.update(user, {"is_active": False})
        await self._log(actor, ActionType.block_user, "user", user_id, reason=reason)
        return UserRead.model_validate(user)

    async def unblock_user(self, user_id: uuid.UUID, actor: User) -> UserRead:
        user = await self._get_user(user_id)
        if user.is_active:
            raise HTTPException(status_code=409, detail="User is not blocked")
        user = await self.user_repo.update(user, {"is_active": True})
        await self._log(actor, ActionType.unblock_user, "user", user_id)
        return UserRead.model_validate(user)

    # ── reports ───────────────────────────────────────────────────────────

    async def create_report(
        self, data: ReportCreate, reporter_id: uuid.UUID
    ) -> ReportRead:
        report = await self.report_repo.create(
            Report(
                reporter_id=reporter_id,
                target_type=data.target_type,
                target_id=data.target_id,
                reason=data.reason,
                description=data.description,
            )
        )
        return ReportRead.model_validate(report)

    async def list_reports(
        self, status: str | None, page: int, size: int
    ) -> ReportPage:
        size = min(size, _PAGE_MAX)
        offset = (page - 1) * size
        reports, total = await self.report_repo.list_all(status, offset, size)
        return ReportPage(
            items=[ReportRead.model_validate(r) for r in reports],
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(reports)) < total,
        )

    async def review_report(self, report_id: uuid.UUID, reviewer: User) -> ReportRead:
        report = await self._get_report(report_id)
        if report.status != ReportStatus.pending:
            raise HTTPException(status_code=409, detail="Report already processed")
        report = await self.report_repo.update(
            report,
            {
                "status": ReportStatus.reviewed,
                "reviewed_by": reviewer.id,
                "reviewed_at": datetime.now(UTC),
            },
        )
        await self._log(reviewer, ActionType.resolve_report, "report", report_id)
        return ReportRead.model_validate(report)

    async def dismiss_report(self, report_id: uuid.UUID, reviewer: User) -> ReportRead:
        report = await self._get_report(report_id)
        if report.status != ReportStatus.pending:
            raise HTTPException(status_code=409, detail="Report already processed")
        report = await self.report_repo.update(
            report,
            {
                "status": ReportStatus.dismissed,
                "reviewed_by": reviewer.id,
                "reviewed_at": datetime.now(UTC),
            },
        )
        await self._log(reviewer, ActionType.dismiss_report, "report", report_id)
        return ReportRead.model_validate(report)

    # ── recipes ───────────────────────────────────────────────────────────

    async def list_recipes_admin(self, page: int, size: int) -> AdminRecipePage:
        size = min(size, _PAGE_MAX)
        offset = (page - 1) * size
        recipes, total = await self.recipe_repo.list_all_admin(offset, size)
        return AdminRecipePage(
            items=[AdminRecipeRead.model_validate(r) for r in recipes],
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(recipes)) < total,
        )

    async def hide_recipe(
        self, recipe_id: uuid.UUID, actor: User, reason: str | None
    ) -> AdminRecipeRead:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if recipe.is_hidden:
            raise HTTPException(status_code=409, detail="Recipe is already hidden")
        recipe = await self.recipe_repo.update(recipe, {"is_hidden": True})
        await self._log(
            actor, ActionType.hide_recipe, "recipe", recipe_id, reason=reason
        )
        return AdminRecipeRead.model_validate(recipe)

    async def unhide_recipe(self, recipe_id: uuid.UUID, actor: User) -> AdminRecipeRead:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if not recipe.is_hidden:
            raise HTTPException(status_code=409, detail="Recipe is not hidden")
        recipe = await self.recipe_repo.update(recipe, {"is_hidden": False})
        await self._log(actor, ActionType.unhide_recipe, "recipe", recipe_id)
        return AdminRecipeRead.model_validate(recipe)

    # ── comments ──────────────────────────────────────────────────────────

    async def list_comments_admin(self, page: int, size: int) -> AdminCommentPage:
        size = min(size, _PAGE_MAX)
        offset = (page - 1) * size
        comments, total = await self.comment_repo.list_all_admin(offset, size)
        return AdminCommentPage(
            items=[AdminCommentRead.model_validate(c) for c in comments],
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(comments)) < total,
        )

    # ── audit log ─────────────────────────────────────────────────────────

    async def list_audit(self, page: int, size: int) -> AuditPage:
        size = min(size, _PAGE_MAX)
        offset = (page - 1) * size
        actions, total = await self.audit_repo.list_all(offset, size)
        return AuditPage(
            items=[ModerationActionRead.model_validate(a) for a in actions],
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(actions)) < total,
        )

    # ── helpers ───────────────────────────────────────────────────────────

    async def _get_user(self, user_id: uuid.UUID) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def _get_report(self, report_id: uuid.UUID) -> Report:
        report = await self.report_repo.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report

    async def _log(
        self,
        actor: User,
        action_type: ActionType,
        target_type: str,
        target_id: uuid.UUID,
        reason: str | None = None,
        meta: dict | None = None,
    ) -> None:
        await self.audit_repo.create(
            ModerationAction(
                moderator_id=actor.id,
                action_type=action_type,
                target_type=target_type,
                target_id=target_id,
                reason=reason,
                meta=meta,
            )
        )
