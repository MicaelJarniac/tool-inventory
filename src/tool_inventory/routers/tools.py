"""Tool Inventory Router.

This module contains the API routes for managing tools in the tool inventory.
It provides endpoints for creating, reading, and updating tools.
"""

from __future__ import annotations

__all__: list[str] = ["router"]

from typing import Annotated
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from tool_inventory.connections import Database, engine
from tool_inventory.models import Tool, ToolCreate, ToolPatch, User  # noqa: TC001
from tool_inventory.users import current_active_user

router = APIRouter(prefix="/api/tool")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a tool",
)
async def create_tool(
    user: Annotated[User, Depends(current_active_user)],
    tool: ToolCreate,
) -> Tool:
    """Create a new tool.

    Args:
        user: The current user.
        tool: The tool creation model.

    Returns:
        The created tool.
    """
    with Session(engine) as session:
        db = Database(session)
        return db.create_tool(user=user, tool=tool.to_model())


@router.get(
    "/{tool_id}",
    summary="Get a tool by ID",
)
async def get_tool_by_id(
    user: Annotated[User, Depends(current_active_user)],
    tool_id: UUID,
) -> Tool:
    """Get a tool by its ID.

    Args:
        user: The current user.
        tool_id: The UUID of the tool.

    Returns:
        The tool with the specified ID.
    """
    with Session(engine) as session:
        db = Database(session)
        return db.get_tool_by_id(user=user, tool_id=tool_id)


@router.get(
    "/",
    summary="Get tools",
)
async def get_tools(
    user: Annotated[User, Depends(current_active_user)],
    name: str | None = None,
) -> list[Tool]:
    """Get tools by name.

    Args:
        user: The current user.
        name: The name of the tool to filter by.

    Returns:
        A list of tools.
    """
    with Session(engine) as session:
        db = Database(session)
        return db.get_tools(user=user, name=name)


@router.patch(
    "/{tool_id}",
    summary="Update a tool",
)
async def update_tool(
    user: Annotated[User, Depends(current_active_user)],
    tool_id: UUID,
    tool_patch: ToolPatch,
) -> Tool:
    """Update an existing tool.

    Args:
        user: The current user.
        tool_id: The UUID of the tool to update.
        tool_patch: The tool patch model.

    Returns:
        The updated tool.
    """
    with Session(engine) as session:
        db = Database(session)
        tool = db.get_tool_by_id(user=user, tool_id=tool_id)
        tool_patch.patch(tool)
        return db.update_tool(user=user, tool=tool)
