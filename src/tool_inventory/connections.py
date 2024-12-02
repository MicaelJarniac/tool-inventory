"""Connections.

This module contains the database connection and operations for the tool inventory
application.
It includes classes for handling database operations and custom exceptions for error
handling.
"""

from __future__ import annotations

__all__: list[str] = [
    "Database",
    "ObjectExistsError",
    "ObjectNotFoundError",
    "ToolExistsError",
    "ToolNotFoundError",
    "create_db_and_tables",
    "engine",
    "get_access_token_db",
    "get_session",
    "get_user_db",
]

from collections.abc import Generator  # noqa: TC003
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import Depends
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from fastapi_users_db_sqlmodel.access_token import SQLModelAccessTokenDatabase
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, SQLModel, create_engine, select
from thefuzz import fuzz  # type: ignore[import-untyped]

from tool_inventory.models import AccessToken, Tool, User

if TYPE_CHECKING:
    from uuid import UUID


class ObjectNotFoundError(Exception):
    """Object not found error."""

    def __init__(self, object_id: UUID, /) -> None:
        """Initialize object not found error.

        Args:
            object_id: The UUID of the object.
        """
        self.object_id = object_id
        self.detail = "Object not found"


class ToolNotFoundError(ObjectNotFoundError):
    """Tool not found error."""

    def __init__(self, tool_id: UUID, /) -> None:
        """Initialize tool not found error.

        Args:
            tool_id: The UUID of the tool.
        """
        super().__init__(tool_id)
        self.detail = "Tool not found"


class ObjectExistsError(Exception):
    """Object exists error."""

    def __init__(self, object_id: UUID, /) -> None:
        """Initialize object exists error.

        Args:
            object_id: The UUID of the object.
        """
        self.object_id = object_id
        self.detail = "Object already exists"


class ToolExistsError(ObjectExistsError):
    """Tool exists error."""

    def __init__(self, tool_id: UUID, /) -> None:
        """Initialize tool exists error.

        Args:
            tool_id: The UUID of the tool.
        """
        super().__init__(tool_id)
        self.detail = "Tool already exists"


class Database:
    """Database connection."""

    def __init__(self, session: Session, /) -> None:
        """Initialize database connection.

        Args:
            session: The database session.
        """
        self.session = session

    def get_tool_by_id(self, user: User, tool_id: UUID) -> Tool:
        """Get a tool by ID.

        Args:
            user: The user.
            tool_id: The UUID of the tool.

        Returns:
            The tool with the specified ID.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        statement = select(Tool).where(
            Tool.created_by_user_id == user.id,
            Tool.id == tool_id,
        )
        result = self.session.exec(statement)
        try:
            return result.one()
        except NoResultFound as err:
            raise ToolNotFoundError(tool_id) from err

    def get_tools(self, user: User, name: str | None = None) -> list[Tool]:
        """Get tools.

        Args:
            user: The user.
            name: The name of the tool to filter by.

        Returns:
            A list of tools.
        """
        statement = select(Tool).where(Tool.created_by_user_id == user.id)
        if name:
            statement = statement.where(Tool.name == name)
        result = self.session.exec(statement)
        return list(result.all())

    def search_tools(self, user: User, query: str) -> list[Tool]:
        """Search tools.

        Args:
            user: The user.
            query: The search query.

        Returns:
            A list of tools.
        """
        statement = select(Tool).where(Tool.created_by_user_id == user.id)
        result = self.session.exec(statement)
        matches: list[tuple[int, Tool]] = []
        for tool in result.all():
            if (score := fuzz.ratio(query.lower(), tool.name.lower())) > 50:  # noqa: PLR2004
                matches.append((score, tool))  # noqa: PERF401
        return [tool for _, tool in sorted(matches, reverse=True)]

    def create_tool(self, user: User, tool: Tool) -> Tool:
        """Create a tool.

        Args:
            user: The user.
            tool: The tool to create.

        Returns:
            The created tool.

        Raises:
            ToolExistsError: If the tool already exists.
        """
        tool.created_by_user_id = user.id
        Tool.model_validate(tool)
        self.session.add(tool)
        try:
            self.session.commit()
        except IntegrityError as err:
            raise ToolExistsError(tool.id) from err
        self.session.refresh(tool)
        return tool

    def update_tool(self, user: User, tool: Tool) -> Tool:
        """Update a tool.

        Args:
            user: The user.
            tool: The tool to update.

        Returns:
            The updated tool.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        if tool.created_by_user_id != user.id:
            raise ToolNotFoundError(tool.id)
        Tool.model_validate(tool)
        self.session.add(tool)
        try:
            self.session.commit()
        except IntegrityError as err:
            raise ToolNotFoundError(tool.id) from err
        self.session.refresh(tool)
        return tool

    def delete_tool(self, user: User, tool_id: UUID) -> None:
        """Delete a tool.

        Args:
            user: The user.
            tool_id: The UUID of the tool to delete.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        tool = self.get_tool_by_id(user=user, tool_id=tool_id)
        self.session.delete(tool)
        self.session.commit()


engine = create_engine("sqlite:///tools.db", echo=True)


def create_db_and_tables() -> None:
    """Create the database and tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    """Get a database session.

    Returns:
        A database session.
    """
    with Session(engine) as session:
        yield session


def get_user_db(
    session: Annotated[Session, Depends(get_session)],
) -> Generator[SQLModelUserDatabase[User, UUID]]:
    """Get a user database.

    Args:
        session: The database session.

    Returns:
        A user database.
    """
    yield SQLModelUserDatabase(session=session, user_model=User)


def get_access_token_db(
    session: Annotated[Session, Depends(get_session)],
) -> Generator[SQLModelAccessTokenDatabase[AccessToken]]:
    """Get an access token database.

    Args:
        session: The database session.

    Returns:
        An access token database.
    """
    yield SQLModelAccessTokenDatabase(session=session, access_token_model=AccessToken)
