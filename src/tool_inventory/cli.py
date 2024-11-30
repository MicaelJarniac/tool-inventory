"""Tool Inventory CLI."""

from __future__ import annotations

__all__ = ["app"]

import typer

app = typer.Typer()


@app.command()
def start() -> None:
    """Start the web server."""
    import uvicorn

    uvicorn.run("tool_inventory.main:app")


@app.callback()
def callback() -> None:
    """Tool Inventory CLI."""


if __name__ == "__main__":
    app()
