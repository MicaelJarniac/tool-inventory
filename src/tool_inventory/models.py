"""Models."""

#' from __future__ import annotations

__all__: list[str] = ["Tool"]

from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Tool(SQLModel, table=True):
    """Tool model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    quantity: int = Field(default=0, ge=0)
    description: str | None = None
    image: str | None = None
