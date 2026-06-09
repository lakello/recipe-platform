import uuid

from fastapi import HTTPException

from app.models.ingredient_category import IngredientCategory
from app.repositories.ingredient_category import IngredientCategoryRepository
from app.schemas.ingredient_category import (
    IngredientCategoryCreate,
    IngredientCategoryRead,
    IngredientCategoryUpdate,
)


class IngredientCategoryService:
    def __init__(self, repo: IngredientCategoryRepository) -> None:
        self.repo = repo

    async def list_categories(self) -> list[IngredientCategoryRead]:
        categories = await self.repo.list_all()
        return [IngredientCategoryRead.model_validate(c) for c in categories]

    async def create_category(
        self, data: IngredientCategoryCreate
    ) -> IngredientCategoryRead:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise HTTPException(status_code=409, detail="Category already exists")
        category = await self.repo.create(IngredientCategory(name=data.name))
        return IngredientCategoryRead.model_validate(category)

    async def update_category(
        self, category_id: uuid.UUID, data: IngredientCategoryUpdate
    ) -> IngredientCategoryRead:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        updates = data.model_dump(exclude_unset=True)
        if "name" in updates:
            existing = await self.repo.get_by_name(updates["name"])
            if existing and existing.id != category_id:
                raise HTTPException(status_code=409, detail="Category already exists")
        category = await self.repo.update(category, updates)
        return IngredientCategoryRead.model_validate(category)

    async def delete_category(self, category_id: uuid.UUID) -> None:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        await self.repo.delete(category)
