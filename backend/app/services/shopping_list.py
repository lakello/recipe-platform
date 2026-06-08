import uuid
from datetime import date, timedelta

from fastapi import HTTPException

from app.models.shopping_list import ShoppingListItem
from app.repositories.shopping_list import ShoppingListRepository
from app.schemas.shopping_list import (
    GenerateRequest,
    ShoppingListItemCreate,
    ShoppingListItemRead,
    ShoppingListItemUpdate,
    ShoppingListRead,
)

# Units that can be normalized to a common base unit for comparison
_NORMALIZE: dict[str, tuple[str, float]] = {
    "kg": ("g", 1000.0),
    "l": ("ml", 1000.0),
}


def normalize_amount(amount: float, unit: str) -> tuple[float, str]:
    """Convert to base unit (g or ml) for numeric comparison."""
    if unit in _NORMALIZE:
        base_unit, factor = _NORMALIZE[unit]
        return amount * factor, base_unit
    return amount, unit


def denormalize_amount(amount: float, base_unit: str) -> tuple[float, str]:
    """Convert large base-unit values to friendlier display units."""
    if base_unit == "g" and amount >= 1000:
        return round(amount / 1000, 3), "kg"
    if base_unit == "ml" and amount >= 1000:
        return round(amount / 1000, 3), "l"
    return round(amount, 2), base_unit


def _dates_for_mode(mode: str, custom_dates: list[date] | None) -> list[date]:
    today = date.today()
    if mode == "today":
        return [today]
    if mode == "week":
        return [today + timedelta(days=i) for i in range(7)]
    if not custom_dates:
        raise HTTPException(status_code=400, detail="dates required for custom mode")
    return custom_dates


class ShoppingListService:
    def __init__(self, repo: ShoppingListRepository) -> None:
        self.repo = repo

    async def get_list(self, user_id: uuid.UUID) -> ShoppingListRead:
        sl = await self.repo.get_or_create_list(user_id)
        return ShoppingListRead.model_validate(sl)

    async def generate(
        self, user_id: uuid.UUID, request: GenerateRequest
    ) -> ShoppingListRead:
        dates = _dates_for_mode(request.mode, request.dates)

        meal_items = await self.repo.get_meal_plan_items_for_dates(user_id, dates)

        # Aggregate ingredient amounts from the meal plan
        # ingredient_id → {amount_base, base_unit, name}
        aggregated: dict[uuid.UUID, dict] = {}
        no_amount_ids: dict[uuid.UUID, str] = {}  # ingredient_id → name

        for mp_item in meal_items:
            recipe = mp_item.recipe
            for ri in recipe.ingredients:
                if ri.amount is None or ri.unit is None:
                    no_amount_ids.setdefault(ri.ingredient_id, ri.ingredient.name)
                    continue
                scaled = float(ri.amount) * mp_item.servings
                norm_amount, base_unit = normalize_amount(scaled, ri.unit.value)

                if ri.ingredient_id in aggregated:
                    if aggregated[ri.ingredient_id]["base_unit"] == base_unit:
                        aggregated[ri.ingredient_id]["amount"] += norm_amount
                    # Different base unit for same ingredient — skip
                else:
                    aggregated[ri.ingredient_id] = {
                        "amount": norm_amount,
                        "base_unit": base_unit,
                        "name": ri.ingredient.name,
                    }

        sl = await self.repo.get_or_create_list(user_id)

        # Smart merge: ingredients with amounts
        for ingredient_id, gen in aggregated.items():
            gen_amount = gen["amount"]
            base_unit = gen["base_unit"]
            existing = await self.repo.get_item_by_ingredient(sl.id, ingredient_id)

            if existing and existing.amount is not None and existing.unit:
                ex_norm, ex_base = normalize_amount(
                    float(existing.amount), existing.unit
                )
                if ex_base != base_unit:
                    # Different unit families — add as separate item
                    final_amount, final_unit = denormalize_amount(gen_amount, base_unit)
                    await self.repo.add_item(
                        sl.id,
                        gen["name"],
                        ingredient_id=ingredient_id,
                        amount=final_amount,
                        unit=final_unit,
                    )
                elif ex_norm < gen_amount:
                    # Need more — update to generated amount
                    final_amount, final_unit = denormalize_amount(gen_amount, base_unit)
                    await self.repo.update_item(
                        existing, {"amount": final_amount, "unit": final_unit}
                    )
                # else: existing >= generated, no change
            elif existing:
                # Existing item has no amount — just leave it
                pass
            else:
                final_amount, final_unit = denormalize_amount(gen_amount, base_unit)
                await self.repo.add_item(
                    sl.id,
                    gen["name"],
                    ingredient_id=ingredient_id,
                    amount=final_amount,
                    unit=final_unit,
                )

        # Ingredients with no amount (to_taste, pinch) — add if not already present
        for ingredient_id, name in no_amount_ids.items():
            if ingredient_id not in aggregated:
                existing = await self.repo.get_item_by_ingredient(sl.id, ingredient_id)
                if not existing:
                    await self.repo.add_item(sl.id, name, ingredient_id=ingredient_id)

        await self.repo.update_generated_at(sl)

        refreshed = await self.repo.get_list(user_id)
        return ShoppingListRead.model_validate(refreshed)

    async def add_item(
        self, user_id: uuid.UUID, data: ShoppingListItemCreate
    ) -> ShoppingListItemRead:
        sl = await self.repo.get_or_create_list(user_id)
        item = await self.repo.add_item(
            shopping_list_id=sl.id,
            ingredient_id=data.ingredient_id,
            name=data.name,
            amount=data.amount,
            unit=data.unit,
            is_manual=True,
        )
        return ShoppingListItemRead.model_validate(item)

    async def update_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID, data: ShoppingListItemUpdate
    ) -> ShoppingListItemRead:
        item = await self._get_owned_item(user_id, item_id)
        updates = data.model_dump(exclude_unset=True)
        item = await self.repo.update_item(item, updates)
        return ShoppingListItemRead.model_validate(item)

    async def delete_item(self, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
        item = await self._get_owned_item(user_id, item_id)
        await self.repo.delete_item(item)

    async def _get_owned_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> ShoppingListItem:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.shopping_list.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return item
