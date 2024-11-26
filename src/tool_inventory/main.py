"""Tool Inventory API."""

from __future__ import annotations

__all__: list[str] = ["app"]

import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from tool_inventory.connections import ObjectExistsError, ObjectNotFoundError
from tool_inventory.routers import tools

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    yield


app = FastAPI(lifespan=lifespan)


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


app.include_router(tools.router)
