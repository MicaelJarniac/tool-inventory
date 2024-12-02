"""Security module for Tool Inventory."""

from __future__ import annotations

__all__: list[str] = [
    "UserManager",
    "auth_backend",
    "cookie_transport",
    "current_active_user",
    "fastapi_users",
    "get_database_strategy",
    "get_user_manager",
]

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users_db_sqlmodel import SQLModelUserDatabase

from tool_inventory.connections import get_access_token_db, get_user_db
from tool_inventory.models import AccessToken, User

cookie_transport = CookieTransport(cookie_max_age=3600)


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken],
        Depends(get_access_token_db),
    ],
) -> DatabaseStrategy[User, UUID, AccessToken]:
    """Get the database strategy.

    Args:
        access_token_db: The access token database.

    Returns:
        The database strategy.
    """
    return DatabaseStrategy(database=access_token_db, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """User manager."""


def get_user_manager(
    user_db: Annotated[SQLModelUserDatabase[User, UUID], Depends(get_user_db)],
) -> UserManager:
    """Get the user manager.

    Args:
        user_db: The user database.

    Returns:
        The user manager.
    """
    return UserManager(user_db)


fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
