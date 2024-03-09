import typer


def repos_callback(ctx: typer.Context, value: list[str]) -> list[str]:
    owner: str = ctx.params.get("owner", "")
    invalid_repos: list[str] = [
        repo
        for repo in value
        if repo.count("/") != (0 if owner else 1)
        or repo.startswith("/")
        or repo.endswith("/")
    ]
    if invalid_repos:
        raise typer.BadParameter(", ".join(invalid_repos))

    return value


def owner_callback(value: str) -> str:
    if value and value.count("/") > 0 or value.startswith("/") or value.endswith("/"):
        raise typer.BadParameter(value)

    return value
