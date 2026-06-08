import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_user
from app.db.session import get_db
from app.models.recipe import Difficulty
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.search import SearchParams, SearchResult
from app.services.recipe import RecipeService
from app.services.search import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])


def _recipe_service(session: AsyncSession = Depends(get_db)) -> RecipeService:
    return RecipeService(
        RecipeRepository(session),
        LikeRepository(session),
        FavoriteRepository(session),
        CommentRepository(session),
    )


@router.get("/recipes", response_model=SearchResult)
async def search_recipes(
    request: Request,
    q: Annotated[str | None, Query()] = None,
    category_id: Annotated[uuid.UUID | None, Query()] = None,
    min_time: Annotated[int | None, Query(gt=0)] = None,
    max_time: Annotated[int | None, Query(gt=0)] = None,
    difficulty: Annotated[Difficulty | None, Query()] = None,
    include_ingredients: Annotated[list[str], Query()] = [],
    exclude_ingredients: Annotated[list[str], Query()] = [],
    sort: Annotated[str, Query()] = "relevance",
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
    recipe_service: RecipeService = Depends(_recipe_service),
    current_user: User | None = Depends(get_optional_user),
) -> SearchResult:
    params = SearchParams(
        q=q,
        category_id=category_id,
        min_time=min_time,
        max_time=max_time,
        difficulty=difficulty,
        include_ingredients=include_ingredients,
        exclude_ingredients=exclude_ingredients,
        sort=sort,  # type: ignore[arg-type]
        page=page,
        size=size,
    )

    search_service = SearchService(request.app.state.os_client)
    ids, total = await search_service.search(params)

    if not ids:
        return SearchResult(total=total, page=page, size=size, items=[])

    user_id = current_user.id if current_user else None
    items = await recipe_service.get_by_ids(ids, user_id)

    return SearchResult(total=total, page=page, size=size, items=items)
