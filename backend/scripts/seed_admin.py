"""Seed a superadmin user for initial setup.

Usage:
    ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=secret python scripts/seed_admin.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User, UserRole


async def seed_admin() -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    password = os.environ.get("ADMIN_PASSWORD", "changeme123")
    username = os.environ.get("ADMIN_USERNAME", "admin")

    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            if existing.role != UserRole.superadmin:
                existing.role = UserRole.superadmin
                existing.is_active = True
                await session.commit()
                print(f"Updated role to superadmin: {email}")
            else:
                print(f"Superadmin already exists: {email}")
            return

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        admin = User(
            email=email,
            username=username,
            password_hash=password_hash,
            is_email_verified=True,
            role=UserRole.superadmin,
        )
        session.add(admin)
        await session.commit()
        print(f"Superadmin created: {email} / {username}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_admin())
