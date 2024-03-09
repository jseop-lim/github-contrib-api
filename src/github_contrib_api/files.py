import csv
from pathlib import Path


def export_pr_count_to_csv(
    pr_count: dict[str, dict[str, int]],
    file_path: Path,
) -> None:
    """Exports a dictionary representing PR counts to a CSV file with totals.

    Args:
        data: A dictionary with repositories as keys and dictionaries mapping user names
            to PR counts as values.
        file_path: The path of the CSV file to save the data to.
    """
    # Gather all unique names and categories
    user_names: list[str] = sorted({
        user_name
        for user_name_to_count in pr_count.values()
        for user_name in user_name_to_count.keys()
    })
    repo_names: list[str] = sorted(pr_count.keys())

    # Compute individual and category totals
    user_totals: dict[str, int] = {
        user_name: sum(
            pr_count[repo_name].get(user_name, 0) for repo_name in repo_names
        )
        for user_name in user_names
    }
    repo_totals: dict[str, int] = {
        repo_name: sum(pr_count[repo_name].values()) for repo_name in repo_names
    }
    grand_total: int = sum(repo_totals.values())

    # Writing to CSV
    with open(file=file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["User", *repo_names, "Total"])

        for user_name in user_names:
            writer.writerow(
                [
                    user_name,
                    *[
                        pr_count[repo_name].get(user_name, 0)
                        for repo_name in repo_names
                    ],
                    user_totals[user_name],
                ],
            )

        # Writing the totals row
        writer.writerow(["Total", *repo_totals.values(), grand_total])
