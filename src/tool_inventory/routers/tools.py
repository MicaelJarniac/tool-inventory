"""Tool Inventory Router."""

from __future__ import annotations

__all__: list[str] = ["router"]

from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, status
from sqlmodel import Session

from tool_inventory.connections import Database, engine
from tool_inventory.models import Tool  # noqa: TC001

router = APIRouter(prefix="/tool")


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    summary="Create a tool",
)
async def create_tool(
    tool: Tool,
) -> Tool:
    """Create a tool."""
    with Session(engine) as session:
        db = Database(session)
        return db.create_tool(tool)


@router.get(
    "/by_id/{tool_id}",
    summary="Get a tool by ID",
)
async def get_tool_by_id(
    tool_id: UUID,
) -> Tool:
    """Get a tool by ID."""
    with Session(engine) as session:
        db = Database(session)
        return db.get_tool_by_id(tool_id)
