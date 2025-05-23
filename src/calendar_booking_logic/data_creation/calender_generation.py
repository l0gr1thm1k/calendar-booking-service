import os
import uuid
import random

from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz

from pathlib import Path
from src.calendar_booking_logic.common.constants import DATA_DIR


def create_randomized_week_calendar(file_path: str, start_date: datetime, user_name: str):
    tz = pytz.timezone("US/Pacific")
    calendar = Calendar()

    for day_offset in range(7):  # One week
        day = start_date + timedelta(days=day_offset)

        # Always busy before 9AM and after 5PM
        outside_busy_times = [(0, 9), (17, 23.9833)]  # 23:59

        for start_hour, end_hour in outside_busy_times:
            start_hr, start_min = int(start_hour), int((start_hour % 1) * 60)
            end_hr, end_min = int(end_hour), int((end_hour % 1) * 60)

            start = tz.localize(datetime(day.year, day.month, day.day, start_hr, start_min))
            end = tz.localize(datetime(day.year, day.month, day.day, end_hr, end_min))
            event = Event()
            event.name = f"{user_name} - Non-working Hours"
            event.begin = start
            event.end = end
            event.uid = str(uuid.uuid4())
            calendar.events.add(event)

        # Random 0 to 8 hours booked (16 blocks of 30 minutes) during work hours
        work_slots = [9 + 0.5 * i for i in range(16)]  # 16 half-hour slots: 09:00–17:00
        slots_filled = random.choice([ii for ii in range(1, 15)])  # at least 1 30 min slot
        busy_blocks = random.sample(work_slots, k=slots_filled)

        for hour in busy_blocks:
            hr = int(hour)
            min_ = int((hour - hr) * 60)
            start = tz.localize(datetime(day.year, day.month, day.day, hr, min_))
            end = start + timedelta(minutes=30)
            event = Event()
            event.name = f"{user_name} - Busy Block"
            event.begin = start
            event.end = end
            event.uid = str(uuid.uuid4())
            calendar.events.add(event)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.writelines(calendar.serialize_iter())


if __name__ == "__main__":
    start_date = datetime.today()
    agents = ["Alex", "Cynthia", "Daniel", "Luis"]

    for name in agents:
        calendar_path = str(Path(DATA_DIR) / f"agent_{name}.ics")
        create_randomized_week_calendar(calendar_path, start_date, name)
