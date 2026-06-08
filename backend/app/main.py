import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.comments import router as comments_router
from app.api.follows import router as follows_router
from app.api.ingredient_categories import router as ingredient_categories_router
from app.api.ingredients import router as ingredients_router
from app.api.likes import router as likes_router
from app.api.meal_plans import router as meal_plans_router
from app.api.oauth import router as oauth_router
from app.api.recipes import router as recipes_router
from app.api.search import router as search_router
from app.api.shopping_list import router as shopping_list_router
from app.api.uploads import router as uploads_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIdMiddleware
from app.core.opensearch import create_opensearch_client, ensure_index_exists
from app.db.session import engine

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    client = create_opensearch_client()
    try:
        await ensure_index_exists(client)
    except Exception as exc:
        logger.warning("OpenSearch not available at startup: %s", exc)
    app.state.os_client = client
    yield
    await client.close()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(users_router)
app.include_router(follows_router)
app.include_router(recipes_router)
app.include_router(likes_router)
app.include_router(comments_router)
app.include_router(categories_router)
app.include_router(ingredient_categories_router)
app.include_router(ingredients_router)
app.include_router(uploads_router)
app.include_router(search_router)
app.include_router(meal_plans_router)
app.include_router(shopping_list_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
async def ready() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready"}
