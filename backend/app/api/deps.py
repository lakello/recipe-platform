from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository

_bearer = HTTPBearer(auto_error=False)
_optional_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = decode_access_token(token)
    user = await UserRepository(session).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role not in (UserRole.admin, UserRole.superadmin):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def get_current_superadmin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    return user


async def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    session: AsyncSession = Depends(get_db),
) -> User | None:
    token = request.cookies.get("access_token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        return None
    try:
        user_id = decode_access_token(token)
    except HTTPException:
        return None
    return await UserRepository(session).get_by_id(user_id)
