import os
import uuid
import random
from pathlib import Path

from ics import Calendar, Event
from datetime import datetime, timedelta
import pytz
from pytz import utc

from src.calendar_booking_logic.common.utils import to_pdt
from src.calendar_booking_logic.common.constants import DATA_DIR
from src.calendar_booking_logic.data_creation.calender_generation import create_randomized_week_calendar

from datetime import datetime, timedelta
from typing import Dict, List

from structlog import get_logger


logger = get_logger(__name__)


class BookingService:
    data_dir = DATA_DIR
    agents = ["Alex", "Cynthia", "Daniel", "Luis"]

    def __init__(self):

        self.calendars = self._load_calendars()

    def _load_calendars(self) -> Dict[str, Dict]:
        self._generate_new_calendars()
        calendars = {}
        for calendar_file_path in os.listdir(self.data_dir):
            if not calendar_file_path.endswith(".ics"):
                continue  # Skip non-ICS files

            full_file_path = str(Path(self.data_dir) / calendar_file_path)
            filename = Path(calendar_file_path).stem
            agent_name = filename.split("_")[1]

            with open(full_file_path, "r") as f:
                calendar = Calendar(f.read())

            calendars[agent_name] = {
                "agent": agent_name,
                "calendar": calendar,
                "filepath": full_file_path
            }

        logger.info(f"Loaded {len(calendars)} calendars for agents {" ".join(list(calendars.keys()))}")

        return calendars

    def _generate_new_calendars(self):
        start_date = datetime.today()
        for name in self.agents:
            calendar_path = str(Path(DATA_DIR) / f"agent_{name}.ics")
            create_randomized_week_calendar(calendar_path, start_date, name)

    def book_appointment(self, agent_id: str, start_time: datetime, duration_minutes: int,
                         title: str = "Appointment") -> None:
        """Books an appointment at the requested time, regardless of conflicts. Always returns True."""
        if agent_id not in self.calendars:
            raise ValueError(f"No calendar loaded for agent {agent_id}")
        pdt_start_time = to_pdt(start_time)
        end_time = pdt_start_time + timedelta(minutes=duration_minutes)

        calendar = self.calendars[agent_id]["calendar"]

        for event in calendar.events:
            if pdt_start_time < event.end.datetime and end_time > event.begin.datetime:
                logger.info(f"Conflict detected with event: {event.name} at {event.begin}–{event.end}")
                break

        new_event = Event()
        new_event.name = title
        new_event.begin = pdt_start_time
        new_event.end = end_time
        calendar.events.add(new_event)

        self.save_calendar_to_file(agent_id)
        logger.info(f"New Calendar event '{title}' for agent '{agent_id}' created.")

    def save_calendar_to_file(self, agent_id):
        file_path = self.calendars[agent_id]["filepath"]
        calendar = self.calendars[agent_id]["calendar"]
        with open(file_path, "w") as f:
            f.writelines(calendar.serialize_iter())






if __name__ == "__main__":
    service = BookingService()
    agent_id = "Luis"
    start_time = datetime(2025, 5, 25, 15, 0)
    duration_minutes = 60
    title = "Test Meeting"

    # Book appointment
    service.book_appointment(agent_id=agent_id,
                             start_time=start_time,
                             duration_minutes=duration_minutes,
                             title=title)