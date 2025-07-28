"""CLI entry point for leenkz."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from typer import Typer

from leenkz.core.config import settings

app = Typer(name="leenkz", help="Leenkz - Keep your links tagged and stored")


@app.command()
def dev(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    log_level: str = "info",
) -> None:
    """Run the development server."""
    uvicorn.run(
        "leenkz.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.command()
def start(
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 1,
    log_level: str = "info",
) -> None:
    """Run the production server."""
    uvicorn.run(
        "leenkz.api.main:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
    )


@app.command()
def migrate() -> None:
    """Run database migrations."""
    from leenkz.core.database import run_migrations

    asyncio.run(run_migrations())


@app.command()
def seed() -> None:
    """Seed the database with sample data."""
    from leenkz.core.seed import seed_database

    asyncio.run(seed_database())


@app.command()
def test() -> None:
    """Run tests."""
    import subprocess

    subprocess.run([sys.executable, "-m", "pytest"], check=True)


@app.command()
def lint() -> None:
    """Run linting."""
    import subprocess

    subprocess.run([sys.executable, "-m", "ruff", "check", "."], check=True)
    subprocess.run([sys.executable, "-m", "black", "--check", "."], check=True)
    subprocess.run([sys.executable, "-m", "mypy", "."], check=True)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main() 