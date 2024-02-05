from aiohttp import ClientSession


async def fetch(
    session: ClientSession,
    url: str,
    headers: dict,
    params: dict,
) -> dict:
    """Asynchronous request to fetch data from URL."""
    async with session.get(url=url, headers=headers, params=params) as response:
        return await response.json()
