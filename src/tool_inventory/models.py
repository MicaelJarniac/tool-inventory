"""Models."""

from __future__ import annotations

__all__: list[str] = [
    "Tool",
    "ToolCreate",
    "ToolPatch",
]

from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic import Field as PydanticField
from sqlmodel import Field, SQLModel


class ToolCreate(BaseModel):
    """Tool creation model."""

    name: str = PydanticField(min_length=1)
    quantity: int = PydanticField(ge=0)
    description: str = ""
    image: str = ""

    def to_model(self) -> Tool:
        """Convert to a tool model."""
        tool = Tool(
            name=self.name.strip(),
            quantity=self.quantity,
            description=self.description.strip(),
            image=self.image.strip(),
        )
        Tool.model_validate(tool)
        return tool


class Tool(SQLModel, table=True):
    """Tool model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False, min_length=1)
    quantity: int = Field(default=0, ge=0)
    description: str = ""
    image: str = ""


class ToolPatch(BaseModel):
    """Tool patch model."""

    name: str | None = None
    quantity: int | None = None
    description: str | None = None
    image: str | None = None

    def patch(self, tool: Tool) -> Tool:
        """Patch a tool."""
        if self.name is not None:
            tool.name = self.name
        if self.quantity is not None:
            tool.quantity = self.quantity
        if self.description is not None:
            tool.description = self.description
        if self.image is not None:
            tool.image = self.image
        return tool
