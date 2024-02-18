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
):
    """Get a list of pushed repository names between start-date and end-date."""
    # TODO: Remove this line
    print(owner_name, github_token, start_datetime, end_datetime)


@app.command()
def pr():  # TODO: Add command arguments and options
    """Get a list of merged PR counts between start-date and end-date."""


def main() -> None:
    app()
