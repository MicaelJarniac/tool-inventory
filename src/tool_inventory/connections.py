"""Connections.

This module contains the database connection and operations for the tool inventory
application.
It includes classes for handling database operations and custom exceptions for error
handling.

Classes:
    - ObjectNotFoundError: Exception raised when an object is not found.
    - ToolNotFoundError: Exception raised when a tool is not found.
    - ObjectExistsError: Exception raised when an object already exists.
    - ToolExistsError: Exception raised when a tool already exists.
    - Database: Class for handling database operations.

Functions:
    - setup_database: Setup the database.
"""

from __future__ import annotations

__all__: list[str] = [
    "Database",
    "ObjectExistsError",
    "ObjectNotFoundError",
    "ToolExistsError",
    "ToolNotFoundError",
    "engine",
    "setup_database",
]

from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import SQLModel, create_engine, select
from thefuzz import fuzz

from tool_inventory.models import Tool

if TYPE_CHECKING:
    from uuid import UUID

    from sqlmodel import Session


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

    def get_tool_by_id(self, tool_id: UUID, /) -> Tool:
        """Get a tool by ID.

        Args:
            tool_id: The UUID of the tool.

        Returns:
            The tool with the specified ID.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        statement = select(Tool).where(Tool.id == tool_id)
        result = self.session.exec(statement)
        try:
            return result.one()
        except NoResultFound as err:
            raise ToolNotFoundError(tool_id) from err

    def get_tools(self, name: str | None = None) -> list[Tool]:
        """Get tools.

        Args:
            name: The name of the tool to filter by.

        Returns:
            A list of tools.
        """
        statement = select(Tool)
        if name:
            statement = statement.where(Tool.name == name)
        result = self.session.exec(statement)
        return list(result.all())

    def search_tools(self, query: str, /) -> list[Tool]:
        """Search tools.

        Args:
            query: The search query.

        Returns:
            A list of tools.
        """
        statement = select(Tool)
        result = self.session.exec(statement)
        matches: list[tuple[int, Tool]] = []
        for tool in result.all():
            if (score := fuzz.ratio(query.lower(), tool.name.lower())) > 50:
                matches.append((score, tool))
        return [tool for _, tool in sorted(matches, reverse=True)]

    def create_tool(self, tool: Tool, /) -> Tool:
        """Create a tool.

        Args:
            tool: The tool to create.

        Returns:
            The created tool.

        Raises:
            ToolExistsError: If the tool already exists.
        """
        Tool.model_validate(tool)
        self.session.add(tool)
        try:
            self.session.commit()
        except IntegrityError as err:
            raise ToolExistsError(tool.id) from err
        self.session.refresh(tool)
        return tool

    def update_tool(self, tool: Tool, /) -> Tool:
        """Update a tool.

        Args:
            tool: The tool to update.

        Returns:
            The updated tool.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        Tool.model_validate(tool)
        self.session.add(tool)
        try:
            self.session.commit()
        except IntegrityError as err:
            raise ToolNotFoundError(tool.id) from err
        self.session.refresh(tool)
        return tool

    def delete_tool(self, tool_id: UUID, /) -> None:
        """Delete a tool.

        Args:
            tool_id: The UUID of the tool to delete.

        Raises:
            ToolNotFoundError: If the tool is not found.
        """
        tool = self.get_tool_by_id(tool_id)
        self.session.delete(tool)
        self.session.commit()


engine = create_engine("sqlite:///tools.db", echo=True)


def setup_database() -> None:
    """Setup database."""
    SQLModel.metadata.create_all(engine)


# Remove this later
setup_database()
