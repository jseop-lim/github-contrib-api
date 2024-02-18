import asyncio
from collections.abc import Coroutine
from datetime import datetime, time
from typing import Annotated, Any
import typer
from rich import print

from .apps import get_repo_names

app = typer.Typer()


@app.command()
def repo(
    owners: Annotated[
        list[str],
        typer.Argument(
            show_default=False,
        ),
    ],
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
        tasks: list[Coroutine[Any, Any, list[str]]] = [
            get_repo_names(
                owner_name=owner_name,
                github_token=github_token,
                start_datetime=datetime.combine(start_datetime, time.min).astimezone(),
                end_datetime=datetime.combine(end_datetime, time.max).astimezone(),
            )
            for owner_name in owners
        ]
        repo_names_list: list[list[str]] = await asyncio.gather(*tasks)

        for owner_name, repo_names in zip(owners, repo_names_list):
            print(f"[bold]{owner_name}:[/bold]")
            for repo_name in sorted(repo_names):
                print(f"  [cyan]{repo_name}[/cyan]")
            print()

    asyncio.run(_repo())


@app.command()
def pr():  # TODO: Add command arguments and options
    """Get a list of merged PR counts between start-date and end-date."""


def main() -> None:
    app()
