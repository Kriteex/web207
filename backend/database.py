# backend/database.py
from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Keep lazy failure for import-time, but DB init will error clearly.
    pass

# Preserve echo=True to maintain original logging behavior.
engine = create_async_engine(DATABASE_URL or "sqlite+aiosqlite://", echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db() -> None:
    """Create all tables on startup (same behavior as before)."""
    if not DATABASE_URL:
        # Fail clearly if DB URL is missing; otherwise run_sync will still attempt sqlite.
        raise RuntimeError("DATABASE_URL is not set.")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession (optional helper; not required by the current app)."""
    async with SessionLocal() as session:
        yield session
