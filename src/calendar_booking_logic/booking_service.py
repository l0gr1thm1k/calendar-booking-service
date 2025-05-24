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
                         title: str = "Appointment") -> dict:
        """Books an appointment at the requested time, regardless of conflicts. Always returns True."""
        if agent_id not in self.calendars:
            raise ValueError(f"No calendar loaded for agent {agent_id}")
        pdt_start_time = to_pdt(start_time)
        end_time = pdt_start_time + timedelta(minutes=duration_minutes)

        calendar = self.calendars[agent_id]["calendar"]
        event_response = {"conflict_info": "No Conflicts",
                          "booking_info": ""}

        for event in calendar.events:
            if pdt_start_time < event.end.datetime and end_time > event.begin.datetime:
                conflict_message = f"Conflict detected with event: {event.name} at {event.begin}–{event.end}"
                logger.info(conflict_message)
                event_response['conflict_info'] = conflict_message

                break

        new_event = Event()
        new_event.name = title
        new_event.begin = pdt_start_time
        new_event.end = end_time
        calendar.events.add(new_event)

        self.save_calendar_to_file(agent_id)
        event_info_message = f"New Calendar event '{title}' for agent '{agent_id}' created."
        logger.info(event_info_message)
        event_response['booking_info'] = event_info_message

        return event_response

    def save_calendar_to_file(self, agent_id):
        file_path = self.calendars[agent_id]["filepath"]
        calendar = self.calendars[agent_id]["calendar"]
        with open(file_path, "w") as f:
            f.writelines(calendar.serialize_iter())

    def find_available_times(self, agent_id: str, date_range_start: datetime, date_range_end: datetime,
                             duration_minutes: int, max_slots: int = 5) -> List[Dict]:
        if agent_id not in self.calendars:
            raise ValueError(f"No calendar loaded for agent {agent_id}")

        calendar = self.calendars[agent_id]["calendar"]
        pdt_date_range_start = to_pdt(date_range_start)
        pdt_date_range_end = to_pdt(date_range_end)
        slots = []
        step = timedelta(minutes=30)
        current = pdt_date_range_start

        # Convert all event ranges to a list of tuples for comparison
        busy_times = [(event.begin.datetime, event.end.datetime) for event in calendar.events]

        while current + timedelta(minutes=duration_minutes) <= pdt_date_range_end and len(slots) < max_slots:
            slot_end = current + timedelta(minutes=duration_minutes)
            conflict = any(start < slot_end and end > current for start, end in busy_times)
            if not conflict:
                slots.append({
                    "start": current.isoformat(),
                    "end": slot_end.isoformat()
                })
            current += step

        logger.info(f"Found {len(slots)} time slots for agent {agent_id}: {slots}")

        return slots


if __name__ == "__main__":
    service = BookingService()
    agent_id = "Luis"
    start_time = datetime(2025, 5, 24, 15, 0)
    end_time = datetime(2025, 5, 28, 17, 30)
    duration_minutes = 90
    title = "Test Meeting"

    # Book appointment
    print(service.find_available_times(agent_id=agent_id,
                                       date_range_start=start_time,
                                       date_range_end=end_time,
                                       duration_minutes=duration_minutes,
                                       max_slots=5))
