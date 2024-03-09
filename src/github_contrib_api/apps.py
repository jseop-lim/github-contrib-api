from datetime import datetime

from aiohttp import ClientSession

from .core import fetch
from .types import Repository
from .utils import parse_datetime


async def get_repo_names(
    owner_name: str,
    github_token: str,
    start_datetime: datetime,
    end_datetime: datetime,
) -> list[str]:
    base_url = "https://api.github.com"
    headers = {"Authorization": f"token {github_token}"}

    async with ClientSession() as session:
        repos = await fetch(
            session=session,
            url=f"{base_url}/orgs/{owner_name}/repos",
            headers=headers,
            params={
                "type": "all",
                "sort": "pushed",
                "direction": "desc",
                "per_page": 100,
                "page": 1,
            },
        )

    repo_names = [
        repo["name"]
        for repo in repos
        if start_datetime <= parse_datetime(repo["pushed_at"]) <= end_datetime
    ]
    return repo_names


async def get_merged_pr_count(
    repo_tuple: Repository,
    github_token: str,
    start_datetime: datetime,
    end_datetime: datetime,
) -> dict[str, int]:
    """PR 관련 지표를 구한다.

    - 각 팀원이 GitHub 저장소에 생성하고 병합한 PR 수
    """
    base_url = "https://api.github.com"
    merged_pr_counts = {}
    headers = {"Authorization": f"token {github_token}"}

    owner_name, repo_name = repo_tuple
    page = 1
    earliest_created_at = end_datetime
    count = 0

    async with ClientSession() as session:
        while earliest_created_at >= start_datetime:
            prs = await fetch(
                session=session,
                url=f"{base_url}/repos/{owner_name}/{repo_name}/pulls",
                headers=headers,
                params={
                    "state": "closed",
                    "sort": "created",
                    "direction": "desc",
                    "page": page,
                    "per_page": 100,
                },
            )

            if not prs or earliest_created_at < start_datetime:
                break

            for pr in prs:
                if (
                    pr["merged_at"]
                    and start_datetime
                    <= parse_datetime(pr["merged_at"])
                    <= end_datetime
                ):
                    user_login = pr["user"]["login"]
                    if user_login not in merged_pr_counts:
                        merged_pr_counts[user_login] = 0
                    merged_pr_counts[user_login] += 1
                    count += 1

            earliest_created_at = parse_datetime(prs[-1]["created_at"])
            page += 1

    print(f"repo: {repo_name:32} | page: {page:4} | count: {count:4}")
    return merged_pr_counts


async def get_pr_review_count(
    owner_name: str,
    repo_names: list[str],
    github_token: str,
    start_datetime: datetime,
    end_datetime: datetime,
) -> dict[str, dict[str, int]]:
    """리뷰 관련 지표를 구한다.

    - review: 각 팀원이 2023년에 회사 GitHub 조직의 모든 저장소의 다른 팀원이 생성한 PR에 작성한 리뷰 수
    - pr: 각 팀원이 2023년에 회사 GitHub 조직의 모든 저장소에 대해 리뷰를 작성한 PR 수 (본인이 생성한 PR은 제외)
    - requested: 각 팀원이 2023년에 회사 GitHub 조직의 모든 저장소에 대해 리뷰를 요청 받은 PR 수
    """
    base_url = "https://api.github.com"
    review_counts = {}
    reviewed_pr_counts = {}
    review_requested_counts = {}
    headers = {"Authorization": f"token {github_token}"}

    async with ClientSession() as session:
        for repo_name in repo_names:
            count = 0
            earliest_created_at = end_datetime
            page = 1
            while earliest_created_at >= start_datetime:
                prs = await fetch(
                    session=session,
                    url=f"{base_url}/repos/{owner_name}/{repo_name}/pulls",
                    headers=headers,
                    params={
                        "state": "all",
                        "sort": "created",
                        "direction": "desc",
                        "page": page,
                        "per_page": 100,
                    },
                )

                if (
                    not prs
                    or not prs[-1]["created_at"]
                    or earliest_created_at < start_datetime
                ):
                    break

                for pr in prs:
                    if not (
                        start_datetime
                        <= parse_datetime(pr["created_at"])
                        <= end_datetime
                    ):
                        continue

                    reviews = await fetch(
                        session=session,
                        url=(
                            f"{base_url}/repos/{owner_name}/{repo_name}"
                            f"/pulls/{pr['number']}/reviews"
                        ),
                        headers=headers,
                        params={
                            "page": 1,
                            "per_page": 100,
                        },
                    )

                    for review in reviews:
                        reviewer = review["user"]["login"]
                        # 본인이 작성한 PR에 단 댓글은 제외
                        if reviewer != pr["user"]["login"]:
                            if reviewer not in review_counts:
                                review_counts[reviewer] = 0
                            review_counts[reviewer] += 1
                            count += 1

                    for reviewer in {review["user"]["login"] for review in reviews}:
                        if reviewer != pr["user"]["login"]:
                            if reviewer not in reviewed_pr_counts:
                                reviewed_pr_counts[reviewer] = 0
                            reviewed_pr_counts[reviewer] += 1

                    for requested_reviewer in pr.get("requested_reviewers", []):
                        reviewer = requested_reviewer["login"]
                        if reviewer not in review_requested_counts:
                            review_requested_counts[reviewer] = 0
                        review_requested_counts[reviewer] += 1

                earliest_created_at = parse_datetime(prs[-1]["created_at"])
                page += 1
            print(f"repo: {repo_name:32} | page: {page:4} | count: {count:4}")

    return {
        "review": review_counts,
        "pr": reviewed_pr_counts,
        "requested": review_requested_counts,
    }
