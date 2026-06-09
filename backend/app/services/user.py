import uuid

import bcrypt
from fastapi import HTTPException

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    return bcrypt.checkpw(plain.encode(), hashed.encode())


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def create_user(self, data: UserCreate) -> UserRead:
        if await self.repository.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if await self.repository.get_by_username(data.username):
            raise HTTPException(status_code=409, detail="Username already taken")
        user = User(
            email=data.email,
            username=data.username,
            password_hash=_hash_password(data.password),
        )
        user = await self.repository.create(user)
        return UserRead.model_validate(user)

    async def get_by_id(self, user_id: uuid.UUID) -> UserRead | None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None
        return UserRead.model_validate(user)

    async def get_by_email(self, email: str) -> UserRead | None:
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        return UserRead.model_validate(user)

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> UserRead:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        updates = data.model_dump(exclude_unset=True)
        if "username" in updates:
            existing = await self.repository.get_by_username(updates["username"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=409, detail="Username already taken")
        user = await self.repository.update(user, updates)
        return UserRead.model_validate(user)
