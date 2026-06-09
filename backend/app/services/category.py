import re
import uuid

from fastapi import HTTPException

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def list_categories(self) -> list[CategoryRead]:
        categories = await self.repository.list_all()
        return [CategoryRead.model_validate(c) for c in categories]

    async def get_category(self, category_id: uuid.UUID) -> CategoryRead:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return CategoryRead.model_validate(category)

    async def create_category(self, data: CategoryCreate) -> CategoryRead:
        slug = _slugify(data.name)
        existing = await self.repository.get_by_slug(slug)
        if existing:
            raise HTTPException(status_code=409, detail="Category already exists")
        category = await self.repository.create(
            Category(name=data.name, slug=slug, description=data.description)
        )
        return CategoryRead.model_validate(category)

    async def update_category(
        self, category_id: uuid.UUID, data: CategoryUpdate
    ) -> CategoryRead:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        updates = data.model_dump(exclude_unset=True)
        if "name" in updates:
            updates["slug"] = _slugify(updates["name"])
            existing = await self.repository.get_by_slug(updates["slug"])
            if existing and existing.id != category_id:
                raise HTTPException(status_code=409, detail="Category already exists")
        category = await self.repository.update(category, updates)
        return CategoryRead.model_validate(category)

    async def delete_category(self, category_id: uuid.UUID) -> None:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        await self.repository.delete(category)
