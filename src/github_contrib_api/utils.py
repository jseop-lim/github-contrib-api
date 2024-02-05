from datetime import datetime


def parse_datetime(datetime_str: str) -> datetime:
    """Parse datetime string to datetime object."""
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z").astimezone()
