"""Connections."""

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

from tool_inventory.models import Tool

if TYPE_CHECKING:
    from uuid import UUID

    from sqlmodel import Session


class ObjectNotFoundError(Exception):
    """Object not found error."""

    def __init__(self, object_id: UUID, /) -> None:
        """Initialize object not found error."""
        self.object_id = object_id
        self.detail = "Object not found"


class ToolNotFoundError(ObjectNotFoundError):
    """Tool not found error."""

    def __init__(self, tool_id: UUID, /) -> None:
        """Initialize tool not found error."""
        super().__init__(tool_id)
        self.detail = "Tool not found"


class ObjectExistsError(Exception):
    """Object exists error."""

    def __init__(self, object_id: UUID, /) -> None:
        """Initialize object exists error."""
        self.object_id = object_id
        self.detail = "Object already exists"


class ToolExistsError(ObjectExistsError):
    """Tool exists error."""

    def __init__(self, tool_id: UUID, /) -> None:
        """Initialize tool exists error."""
        super().__init__(tool_id)
        self.detail = "Tool already exists"


class Database:
    """Database connection."""

    def __init__(self, session: Session, /) -> None:
        """Initialize database connection."""
        self.session = session

    def get_tool_by_id(self, tool_id: UUID, /) -> Tool:
        """Get a tool by ID."""
        statement = select(Tool).where(Tool.id == tool_id)
        result = self.session.exec(statement)
        try:
            return result.one()
        except NoResultFound as err:
            raise ToolNotFoundError(tool_id) from err

    def get_tools(self, name: str | None = None) -> list[Tool]:
        """Get tools."""
        statement = select(Tool)
        if name:
            statement = statement.where(Tool.name == name)
        result = self.session.exec(statement)
        return list(result.all())

    def create_tool(self, tool: Tool, /) -> Tool:
        """Create a tool."""
        Tool.model_validate(tool)
        self.session.add(tool)
        try:
            self.session.commit()
        except IntegrityError as err:
            raise ToolExistsError(tool.id) from err
        self.session.refresh(tool)
        return tool

    def update_tool(self, tool: Tool, /) -> Tool:
        """Update a tool."""
        Tool.model_validate(tool)
        self.session.add(tool)
        try:
            self.session.commit()
        except IntegrityError as err:
            raise ToolNotFoundError(tool.id) from err
        self.session.refresh(tool)
        return tool


engine = create_engine("sqlite:///tools.db", echo=True)


def setup_database() -> None:
    """Setup database."""
    SQLModel.metadata.create_all(engine)


# Remove this later
setup_database()
