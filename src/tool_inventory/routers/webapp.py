"""Webapp router."""

from __future__ import annotations

__all__: list[str] = ["router"]

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse  # noqa: TC002
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from tool_inventory import root
from tool_inventory.connections import Database, engine
from tool_inventory.models import Tool, ToolCreate, ToolPatch

router = APIRouter()
templates = Jinja2Templates(directory=root / "templates")


@router.get("/")
async def web_read_tools(
    request: Request,
) -> HTMLResponse:
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
    with Session(engine) as session:
        db = Database(session)
        db.delete_tool(db.get_tool_by_id(tool_id))
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
