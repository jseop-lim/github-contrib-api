from datetime import datetime
from typing import Annotated
import typer

app = typer.Typer()


@app.command()
def repo(
    owner_name: list[str],
    github_token: Annotated[
        str,
        typer.Option(
            envvar="GITHUB_TOKEN",
            show_default=False,
            prompt=True,
            hide_input=True,
        ),
    ],
    start_date: Annotated[
        datetime,
        typer.Option(
            show_default=False,
            formats=["%Y-%m-%d"],
        ),
    ],
    end_date: Annotated[
        datetime,
        typer.Option(
            default_factory=datetime.now,
            show_default="today",
            formats=["%Y-%m-%d"],
        ),
    ],
):
    """Get a list of pushed repository names between start-date and end-date."""
    print(owner_name, github_token, start_date, end_date)  # TODO: Remove this line


@app.command()
def pr():  # TODO: Add command arguments and options
    """Get a list of merged PR counts between start-date and end-date."""


def main() -> None:
    app()
