"""Webapp router.

This module contains the web routes for the tool inventory application.
It provides endpoints for creating, reading, updating, and deleting tools,
as well as updating tool quantities.

Routes:
    - GET /: Fetch and display all tools.
    - GET /create: Render the tool creation form.
    - POST /create: Create a new tool.
    - GET /edit/{tool_id}: Render the tool edit form.
    - POST /edit/{tool_id}: Edit an existing tool.
    - POST /delete/{tool_id}: Delete a tool.
    - POST /update_quantity/{tool_id}: Update the quantity of a tool.
"""

from __future__ import annotations

__all__: list[str] = ["router"]

from typing import Annotated
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from tool_inventory import root
from tool_inventory.connections import Database, engine
from tool_inventory.models import ToolCreate, ToolPatch

router = APIRouter()
templates = Jinja2Templates(directory=root / "templates")


@router.get("/")
async def web_read_tools(
    request: Request,
) -> HTMLResponse:
    """Fetch and display all tools.

    Args:
        request: The request object.

    Returns:
        An HTML response with the list of tools.
    """
    with Session(engine) as session:
        db = Database(session)
        tools = db.get_tools()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "tools": tools},
        )


@router.get("/create")
async def web_create_tool_form(
    request: Request,
) -> HTMLResponse:
    """Render the tool creation form.

    Args:
        request: The request object.

    Returns:
        An HTML response with the tool creation form.
    """
    return templates.TemplateResponse(
        "tool_form.html",
        {"request": request},
    )


@router.post("/create")
async def web_create_tool(
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
) -> RedirectResponse:
    """Create a new tool.

    Args:
        name: The name of the tool.
        description: The description of the tool.
        quantity: The quantity of the tool.

    Returns:
        A redirect response to the home page.
    """
    with Session(engine) as session:
        db = Database(session)
        db.create_tool(
            ToolCreate(
                name=name,
                description=description,
                quantity=quantity,
            ).to_model(),
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit/{tool_id}")
async def web_edit_tool_form(
    request: Request,
    tool_id: UUID,
) -> HTMLResponse:
    """Render the tool edit form.

    Args:
        request: The request object.
        tool_id: The UUID of the tool to edit.

    Returns:
        An HTML response with the tool edit form.
    """
    with Session(engine) as session:
        db = Database(session)
        return templates.TemplateResponse(
            "tool_form.html",
            {"request": request, "tool": db.get_tool_by_id(tool_id)},
        )


@router.post("/edit/{tool_id}")
async def web_edit_tool(
    tool_id: UUID,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
) -> RedirectResponse:
    """Edit an existing tool.

    Args:
        tool_id: The UUID of the tool to edit.
        name: The new name of the tool.
        description: The new description of the tool.
        quantity: The new quantity of the tool.

    Returns:
        A redirect response to the home page.
    """
    with Session(engine) as session:
        db = Database(session)
        db.update_tool(
            ToolPatch(
                name=name,
                description=description,
                quantity=quantity,
            ).patch(db.get_tool_by_id(tool_id)),
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete/{tool_id}")
async def web_delete_tool(
    tool_id: UUID,
) -> RedirectResponse:
    """Delete a tool.

    Args:
        tool_id: The UUID of the tool to delete.

    Returns:
        A redirect response to the home page.
    """
    with Session(engine) as session:
        db = Database(session)
        db.delete_tool(tool_id)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/update_quantity/{tool_id}")
async def web_update_quantity(
    tool_id: UUID,
    action: Annotated[str, Form()],
) -> RedirectResponse:
    """Update the quantity of a tool.

    Args:
        tool_id: The UUID of the tool to update.
        action: The action to perform (increment or decrement).

    Returns:
        A redirect response to the home page.
    """
    with Session(engine) as session:
        db = Database(session)
        tool = db.get_tool_by_id(tool_id)
        db.update_tool(
            ToolPatch(
                quantity=max(
                    0,
                    tool.quantity + 1 if action == "increment" else tool.quantity - 1,
                ),
            ).patch(tool),
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/search")
async def web_search_tools(
    request: Request,
    query: str,
) -> HTMLResponse:
    """Search for tools.

    Args:
        request: The request object.
        query: The search query.

    Returns:
        An HTML response with the search results.
    """
    with Session(engine) as session:
        db = Database(session)
        tools = db.search_tools(query)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "tools": tools},
        )
