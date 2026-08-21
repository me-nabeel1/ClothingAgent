"""Common shared dependencies."""
from typing import AsyncIterator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import AppConfig, get_config

def get_db_session() -> AsyncIterator[AsyncSession]:
    """Dependency wrapper for database session."""
    return get_db()
