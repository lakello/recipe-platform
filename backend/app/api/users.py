import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserPublicRead, UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


def _user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(session))


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    service: UserService = Depends(_user_service),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return await service.update_user(current_user.id, data)


@router.get("/{user_id}", response_model=UserPublicRead)
async def get_public_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
) -> UserPublicRead:
    user = await UserRepository(session).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublicRead.model_validate(user)
