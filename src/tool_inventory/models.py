"""Models.

This module contains the data models for the tool inventory application.
It includes models for creating, updating, and representing tools.
"""

#' from __future__ import annotations

__all__: list[str] = [
    "AccessToken",
    "Tool",
    "ToolCreate",
    "ToolPatch",
    "User",
]

from uuid import UUID, uuid4

from fastapi_users import schemas
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from pydantic import BaseModel
from pydantic import Field as PydanticField
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModelBaseUserDB, table=True):
    """User model."""

    tools: list["Tool"] = Relationship(back_populates="created_by_user")


class UserRead(schemas.BaseUser[UUID]):
    """User read model."""


class UserCreate(schemas.BaseUserCreate):
    """User creation model."""


class UserUpdate(schemas.BaseUserUpdate):
    """User update model."""


class AccessToken(SQLModelBaseAccessToken, table=True):
    """Access token model."""


class ToolCreate(BaseModel):
    """Tool creation model."""

    name: str = PydanticField(min_length=1)
    quantity: int = PydanticField(ge=0)
    description: str = ""
    image: str = ""

    def to_model(self) -> "Tool":
        """Convert to a tool model.

        Returns:
            The tool model.
        """
        tool = Tool(
            name=self.name.strip(),
            quantity=self.quantity,
            description=self.description.strip(),
            image=self.image.strip(),
        )
        #' Tool.model_validate(tool)
        return tool


class Tool(SQLModel, table=True):
    """Tool model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False, min_length=1)
    quantity: int = Field(default=0, ge=0)
    description: str = ""
    image: str = ""

    created_by_user_id: UUID = Field(foreign_key="user.id", nullable=False)
    created_by_user: User = Relationship(back_populates="tools")


class ToolPatch(BaseModel):
    """Tool patch model."""

    name: str | None = None
    quantity: int | None = None
    description: str | None = None
    image: str | None = None

    def patch(self, tool: Tool) -> Tool:
        """Patch a tool.

        Args:
            tool: The tool to patch.

        Returns:
            The patched tool.
        """
        if self.name is not None:
            tool.name = self.name
        if self.quantity is not None:
            tool.quantity = self.quantity
        if self.description is not None:
            tool.description = self.description
        if self.image is not None:
            tool.image = self.image
        return tool
