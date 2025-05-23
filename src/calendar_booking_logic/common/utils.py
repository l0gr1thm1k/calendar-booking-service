import datetime
from src.calendar_booking_logic.common.constants import PDT


def to_pdt(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return PDT.localize(dt)
    else:
        return dt.astimezone(PDT)