import asyncio
from datetime import datetime, time
from typing import Annotated
import typer

from .apps import get_repo_names

app = typer.Typer()


@app.command()
def repo(
    owner_name: str,  # TODO: list[str] type
    github_token: Annotated[
        str,
        typer.Option(
            envvar="GITHUB_TOKEN",
            show_default=False,
            prompt=True,
            hide_input=True,
        ),
    ],
    start_datetime: Annotated[
        datetime,
        typer.Option(
            "--start-date",
            show_default=False,
            formats=["%Y-%m-%d"],
        ),
    ],
    end_datetime: Annotated[
        datetime,
        typer.Option(
            "--end-date",
            default_factory=datetime.now,
            show_default="today",
            formats=["%Y-%m-%d"],
        ),
    ],
) -> None:
    """Get a list of pushed repository names between start-date and end-date."""

    async def _repo() -> None:
        repo_names: list[str] = await get_repo_names(
            owner_name=owner_name,
            github_token=github_token,
            start_datetime=datetime.combine(start_datetime, time.min).astimezone(),
            end_datetime=datetime.combine(end_datetime, time.max).astimezone(),
        )

        for repo_name in repo_names:
            typer.echo(repo_name)

    asyncio.run(_repo())


@app.command()
def pr():  # TODO: Add command arguments and options
    """Get a list of merged PR counts between start-date and end-date."""


def main() -> None:
    app()
