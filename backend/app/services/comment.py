import uuid

from fastapi import HTTPException

from app.models.comment import Comment
from app.repositories.comment import CommentRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.comment import (
    CommentCreate,
    CommentPage,
    CommentRead,
    CommentUpdate,
)

_PAGE_SIZE_MAX = 50


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        recipe_repo: RecipeRepository,
    ) -> None:
        self.comment_repo = comment_repo
        self.recipe_repo = recipe_repo

    async def add_comment(
        self,
        recipe_id: uuid.UUID,
        author_id: uuid.UUID,
        data: CommentCreate,
    ) -> CommentRead:
        await self._assert_recipe_exists(recipe_id)
        if data.parent_id is not None:
            parent = await self.comment_repo.get_by_id(data.parent_id)
            if not parent or parent.recipe_id != recipe_id:
                raise HTTPException(status_code=404, detail="Parent comment not found")
            if parent.parent_id is not None:
                raise HTTPException(status_code=400, detail="Cannot reply to a reply")
        comment = await self.comment_repo.create(
            Comment(
                recipe_id=recipe_id,
                author_id=author_id,
                parent_id=data.parent_id,
                body=data.body,
            )
        )
        return CommentRead.model_validate(comment)

    async def edit_comment(
        self,
        comment_id: uuid.UUID,
        author_id: uuid.UUID,
        data: CommentUpdate,
    ) -> CommentRead:
        comment = await self._get_owned(comment_id, author_id)
        comment = await self.comment_repo.update(comment, {"body": data.body})
        return CommentRead.model_validate(comment)

    async def delete_comment(self, comment_id: uuid.UUID, author_id: uuid.UUID) -> None:
        comment = await self._get_owned(comment_id, author_id)
        await self.comment_repo.update(comment, {"is_deleted": True})

    async def hide_comment(self, comment_id: uuid.UUID) -> CommentRead:
        comment = await self._get_existing(comment_id)
        comment = await self.comment_repo.update(comment, {"is_hidden": True})
        return CommentRead.model_validate(comment)

    async def unhide_comment(self, comment_id: uuid.UUID) -> CommentRead:
        comment = await self._get_existing(comment_id)
        comment = await self.comment_repo.update(comment, {"is_hidden": False})
        return CommentRead.model_validate(comment)

    async def list_comments(
        self, recipe_id: uuid.UUID, page: int, size: int
    ) -> CommentPage:
        await self._assert_recipe_exists(recipe_id)
        size = min(size, _PAGE_SIZE_MAX)
        offset = (page - 1) * size
        comments, total = await self.comment_repo.list_top_level(
            recipe_id, offset, size
        )
        ids = [c.id for c in comments]
        reply_counts = await self.comment_repo.reply_count_batch(ids)
        items = [
            CommentRead.model_validate(c).model_copy(
                update={"reply_count": reply_counts.get(c.id, 0)}
            )
            for c in comments
        ]
        return CommentPage(
            items=items,
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(comments)) < total,
        )

    async def list_replies(
        self, comment_id: uuid.UUID, page: int, size: int
    ) -> CommentPage:
        parent = await self._get_existing(comment_id)
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=400, detail="Cannot list replies of a reply"
            )
        size = min(size, _PAGE_SIZE_MAX)
        offset = (page - 1) * size
        replies, total = await self.comment_repo.list_replies(comment_id, offset, size)
        items = [CommentRead.model_validate(r) for r in replies]
        return CommentPage(
            items=items,
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(replies)) < total,
        )

    async def _assert_recipe_exists(self, recipe_id: uuid.UUID) -> None:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

    async def _get_existing(self, comment_id: uuid.UUID) -> Comment:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment

    async def _get_owned(self, comment_id: uuid.UUID, author_id: uuid.UUID) -> Comment:
        comment = await self._get_existing(comment_id)
        if comment.is_deleted:
            raise HTTPException(status_code=404, detail="Comment not found")
        if comment.author_id != author_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return comment
