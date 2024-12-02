"""Web app router.

This module contains the web routes for the tool inventory application.
It provides endpoints for creating, reading, updating, and deleting tools,
as well as updating tool quantities.
"""

from __future__ import annotations

__all__: list[str] = ["router"]

from typing import Annotated
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from tool_inventory import root
from tool_inventory.connections import Database, engine
from tool_inventory.models import ToolCreate, ToolPatch, User  # noqa: TC001
from tool_inventory.users import current_active_user

router = APIRouter()
templates = Jinja2Templates(directory=root / "templates")


@router.get("/login")
async def web_login_form(
    request: Request,
) -> HTMLResponse:
    """Render the login form.

    Args:
        request: The request object.

    Returns:
        An HTML response with the login form.
    """
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.get("/register")
async def web_register_form(
    request: Request,
) -> HTMLResponse:
    """Render the registration form.

    Args:
        request: The request object.

    Returns:
        An HTML response with the registration form.
    """
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@router.get("/")
async def web_read_tools(
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
) -> HTMLResponse:
    """Fetch and display all tools.

    Args:
        request: The request object.
        user: The current active user.

    Returns:
        An HTML response with the list of tools.
    """
    with Session(engine) as session:
        db = Database(session)
        tools = db.get_tools(user=user)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "tools": tools, "user": user},
        )


@router.get("/create")
async def web_create_tool_form(
    request: Request,
    user: Annotated[User, Depends(current_active_user)],
) -> HTMLResponse:
    """Render the tool creation form.

    Args:
        request: The request object.
        user: The current active user.

    Returns:
        An HTML response with the tool creation form.
    """
    return templates.TemplateResponse(
        "tool_form.html",
        {"request": request, "user": user},
    )


@router.post("/create")
async def web_create_tool(
    user: Annotated[User, Depends(current_active_user)],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
) -> RedirectResponse:
    """Create a new tool.

    Args:
        user: The current active user.
        name: The name of the tool.
        description: The description of the tool.
        quantity: The quantity of the tool.

    Returns:
        A redirect response to the home page.
    """
    with Session(engine) as session:
        db = Database(session)
        db.create_tool(
            user=user,
            tool=ToolCreate(
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
    user: Annotated[User, Depends(current_active_user)],
) -> HTMLResponse:
    """Render the tool edit form.

    Args:
        request: The request object.
        tool_id: The UUID of the tool to edit.
        user: The current active user.

    Returns:
        An HTML response with the tool edit form.
    """
    with Session(engine) as session:
        db = Database(session)
        return templates.TemplateResponse(
            "tool_form.html",
            {
                "request": request,
                "tool": db.get_tool_by_id(user=user, tool_id=tool_id),
                "user": user,
            },
        )


@router.post("/edit/{tool_id}")
async def web_edit_tool(
    tool_id: UUID,
    user: Annotated[User, Depends(current_active_user)],
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    quantity: Annotated[int, Form()],
) -> RedirectResponse:
    """Edit an existing tool.

    Args:
        tool_id: The UUID of the tool to edit.
        user: The current active user.
        name: The new name of the tool.
        description: The new description of the tool.
        quantity: The new quantity of the tool.

    Returns:
        A redirect response to the home page.
    """
    with Session(engine) as session:
        db = Database(session)
        db.update_tool(
            user=user,
            tool=ToolPatch(
                name=name,
                description=description,
                quantity=quantity,
            ).patch(db.get_tool_by_id(user=user, tool_id=tool_id)),
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/delete/{tool_id}")
async def web_delete_tool(
    request: Request,
    tool_id: UUID,
    user: Annotated[User, Depends(current_active_user)],
) -> HTMLResponse:
    """Delete a tool.

    Args:
        request: The request object.
        tool_id: The UUID of the tool to delete.
        user: The current active user.

    Returns:
        A script to delete the tool.
    """
    with Session(engine) as session:
        db = Database(session)
        db.delete_tool(user=user, tool_id=tool_id)
    return templates.TemplateResponse(
        "delete_tool.html",
        {"request": request, "tool_id": tool_id},
    )


@router.post("/update_quantity/{tool_id}")
async def web_update_quantity(
    request: Request,
    tool_id: UUID,
    action: Annotated[str, Form()],
    user: Annotated[User, Depends(current_active_user)],
) -> HTMLResponse:
    """Update the quantity of a tool.

    Args:
        request: The request object.
        tool_id: The UUID of the tool to update.
        action: The action to perform (increment or decrement).
        user: The current active user.

    Returns:
        A script to update quantity.
    """
    with Session(engine) as session:
        db = Database(session)
        tool = db.get_tool_by_id(user=user, tool_id=tool_id)
        db.update_tool(
            user=user,
            tool=ToolPatch(
                quantity=max(
                    0,
                    tool.quantity + 1 if action == "increment" else tool.quantity - 1,
                ),
            ).patch(tool),
        )
    return templates.TemplateResponse(
        "update_quantity.html",
        {"request": request, "tool_id": tool.id, "quantity": tool.quantity},
    )


@router.get("/search")
async def web_search_tools(
    request: Request,
    query: str,
    user: Annotated[User, Depends(current_active_user)],
) -> HTMLResponse:
    """Search for tools.

    Args:
        request: The request object.
        query: The search query.
        user: The current active user.

    Returns:
        An HTML response with the search results.
    """
    with Session(engine) as session:
        db = Database(session)
        tools = db.search_tools(user=user, query=query)
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "query": query, "tools": tools, "user": user},
        )
