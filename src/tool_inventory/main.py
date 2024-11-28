"""Tool Inventory API."""

from __future__ import annotations

__all__: list[str] = ["app"]

import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import ValidationError

from tool_inventory import root
from tool_inventory.connections import ObjectExistsError, ObjectNotFoundError
from tool_inventory.routers import tools, webapp

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=root / "static"), name="static")


@app.exception_handler(ObjectNotFoundError)
async def object_not_found_error_handler(
    _request: Request,
    exc: ObjectNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail, "object_id": exc.object_id},
    )


@app.exception_handler(ObjectExistsError)
async def object_exists_error_handler(
    _request: Request,
    exc: ObjectExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail, "object_id": exc.object_id},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(
    _request: Request,
    exc: ValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


app.include_router(tools.router)
app.include_router(webapp.router)
