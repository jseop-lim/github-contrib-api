import asyncio
from collections import Counter
from collections.abc import Coroutine
from datetime import datetime, time
from functools import reduce
from operator import iadd
from pathlib import Path
from typing import Annotated, Any

import typer
from rich import print

from .apps import get_merged_pr_count, get_repo_names
from .callbacks import owner_callback, repos_callback
from .files import export_pr_count_to_csv
from .types import Repository

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
            show_default="today",  # type: ignore
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
def pr(
    repos: Annotated[
        list[str],
        typer.Argument(
            callback=repos_callback,
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
            show_default="today",  # type: ignore
            formats=["%Y-%m-%d"],
        ),
    ],
    owner: Annotated[
        str,
        typer.Option(
            callback=owner_callback,
            show_default=False,
        ),
    ] = "",
    csv_output: Annotated[
        Path | None,
        typer.Option(
            show_default=False,
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=False,
            resolve_path=True,
        ),
    ] = None,
) -> None:
    """Get a list of merged PR counts between start-date and end-date."""
    repo_tuples: list[Repository] = (
        [Repository(owner=owner, name=name) for name in repos]
        if owner
        else [
            Repository(owner=name.split("/")[0], name=name.split("/")[1])
            for name in repos
        ]
    )

    async def _repo() -> None:
        print("\n<Merged Pull Requests>")
        tasks: list[Coroutine[Any, Any, dict[str, int]]] = [
            get_merged_pr_count(
                repo_tuple=repo_tuple,
                github_token=github_token,
                start_datetime=datetime.combine(start_datetime, time.min).astimezone(),
                end_datetime=datetime.combine(end_datetime, time.max).astimezone(),
            )
            for repo_tuple in repo_tuples
        ]
        results: list[dict[str, int]] = await asyncio.gather(*tasks)
        merged_pr_count: dict[str, int] = reduce(
            iadd,
            map(Counter, results),  # type: ignore[arg-type]
            Counter(),
        )

        print("\n<Ranking>")
        for rank, d in enumerate(
            sorted(merged_pr_count.items(), key=lambda x: x[1], reverse=True),
            start=1,
        ):
            print(f"{rank:3}. {d[0]:20} {d[1]:4}")

        if csv_output:
            export_pr_count_to_csv(
                pr_count=dict(zip(repos, results)),
                file_path=csv_output,
            )

    asyncio.run(_repo())


def main() -> None:
    app()
