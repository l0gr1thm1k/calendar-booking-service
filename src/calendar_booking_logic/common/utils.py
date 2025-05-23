import datetime
from src.calendar_booking_logic.common.constants import PDT


def to_pdt(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return PDT.localize(dt)
    else:
        return dt.astimezone(PDT)


def parse_datetime(datetime_str: str) -> datetime:
    """
    Converts a datetime string like '2025-05-28 10:30 AM' to a timezone-aware datetime object in PDT.
    """
    naive_dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")

    return to_pdt(naive_dt)