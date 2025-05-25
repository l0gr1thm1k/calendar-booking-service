import os
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List

import pytz
from ics import Calendar, Event
from calendar_booking_logic.common.constants import DATA_DIR, DEFAULT_AGENT_IDENTIFIER
from calendar_booking_logic.common.utils import to_pdt
from calendar_booking_logic.data_creation.calender_generation import create_randomized_week_calendar
from calendar_booking_logic.data_creation.create_calendar_plot import create_workday_schedule_plot
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

        create_workday_schedule_plot(file_path=calendars[DEFAULT_AGENT_IDENTIFIER]["filepath"],
                                     start_date=datetime.today())
        logger.info(f"Loaded {len(calendars)} calendars for agents {' '.join(list(calendars.keys()))}")

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

        pdt_tz = pytz.timezone("US/Pacific")

        for event in calendar.events:
            event_start = event.begin.datetime
            event_end = event.end.datetime

            if event_start.tzinfo is None or event_start.tzinfo.utcoffset(event_start) == timedelta(0):
                event_start = event_start.replace(tzinfo=pytz.UTC).astimezone(pdt_tz)
            if event_end.tzinfo is None or event_end.tzinfo.utcoffset(event_end) == timedelta(0):
                event_end = event_end.replace(tzinfo=pytz.UTC).astimezone(pdt_tz)

            if pdt_start_time < event_end and end_time > event_start:
                conflict_message = f"Conflict detected with event: {event.name} at {event_start}–{event_end}"
                logger.info(conflict_message)
                event_response['conflict_info'] = conflict_message
                break

        new_event = Event()
        new_event.name = title
        new_event.begin = pdt_start_time
        new_event.end = end_time
        calendar.events.add(new_event)

        self.save_calendar_to_file(agent_id)
        create_workday_schedule_plot(file_path=self.calendars[agent_id]["filepath"],
                                     start_date=datetime.today())
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

    def book_heads_down_focus_block(self, agent_id: str, date_range_start: datetime,
                                    date_range_end: datetime) -> dict:
        if agent_id not in self.calendars:
            raise ValueError(f"No calendar loaded for agent {agent_id}")

        calendar = self.calendars[agent_id]["calendar"]

        best_day = self._compute_day_with_least_meeting_time(calendar, date_range_start, date_range_end)

        if best_day is None:
            return self._no_focus_day_response(agent_id, reason="No available day found in range.")

        free_blocks = self._get_free_blocks_for_day(calendar, best_day)

        if not free_blocks:
            return self._no_focus_day_response(agent_id, day=best_day, reason="Best day is fully booked.")

        # 🔁 Only use the longest continuous block of free time
        focus_start, focus_end = self._get_longest_continuous_free_block(free_blocks)

        # 🧮 Count other meetings during work hours on this day
        meeting_count = sum(
            1 for e in calendar.events
            if e.name != "Focus Time"
            and (e.begin.datetime.date() == best_day or e.end.datetime.date() == best_day)
            and e.begin.datetime.time() < time(17, 0)
            and e.end.datetime.time() > time(9, 0)
        )

        self._create_focus_event(calendar, focus_start, focus_end, agent_id)

        focus_hours = round((focus_end - focus_start).total_seconds() / 3600, 2)

        create_workday_schedule_plot(file_path=self.calendars[agent_id]["filepath"],
                                     start_date=datetime.today())

        return {
            "agent_id": agent_id,
            "day": best_day.strftime('%Y-%m-%d'),
            "start": focus_start.isoformat(),
            "end": focus_end.isoformat(),
            "booking_info": (
                f"Focus Time booked from {focus_start.strftime('%H:%M')} to {focus_end.strftime('%H:%M')} "
                f"on {best_day.strftime('%Y-%m-%d')} covering {focus_hours} hours of uninterrupted time."
            ),
            "conflict_info": f"{meeting_count} other meetings were found on this day."
        }

    @staticmethod
    def _compute_day_with_least_meeting_time(calendar, date_range_start, date_range_end):
        tz = pytz.timezone("US/Pacific")
        best_day = None
        min_meeting_minutes = float('inf')

        for offset in range((date_range_end - date_range_start).days + 1):
            day = (date_range_start + timedelta(days=offset)).date()
            work_start = tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=9))
            work_end = tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=17))
            total_busy = 0

            for event in calendar.events:
                if event.begin.datetime.date() != day and event.end.datetime.date() != day:
                    continue
                overlap_start = max(event.begin.datetime, work_start)
                overlap_end = min(event.end.datetime, work_end)
                if overlap_start < overlap_end:
                    total_busy += (overlap_end - overlap_start).total_seconds() / 60

            if total_busy < min_meeting_minutes:
                min_meeting_minutes = total_busy
                best_day = day

        return best_day

    def _get_free_blocks_for_day(self, calendar, day):
        tz = pytz.timezone("US/Pacific")
        work_start = tz.localize(datetime.combine(day, datetime.min.time()) + timedelta(hours=9))
        slots = [work_start + timedelta(minutes=30 * i) for i in range(16)]  # 9–5 in 30-min steps

        busy_ranges = [(event.begin.datetime, event.end.datetime) for event in calendar.events
                       if event.begin.date() == day or event.end.date() == day]

        free_blocks = []
        current_block = []

        for slot_start in slots:
            slot_end = slot_start + timedelta(minutes=30)
            conflict = any(start < slot_end and end > slot_start for start, end in busy_ranges)
            if not conflict:
                current_block.append((slot_start, slot_end))
            else:
                if current_block:
                    free_blocks.append(current_block)
                current_block = []

        if current_block:
            free_blocks.append(current_block)

        return free_blocks

    @staticmethod
    def _merge_time_blocks(blocks):
        return blocks[0][0][0], blocks[-1][-1][1]

    def _create_focus_event(self, calendar, start, end, agent_id):
        event = Event()
        event.name = "Focus Time"
        event.begin = start
        event.end = end
        calendar.events.add(event)
        self.save_calendar_to_file(agent_id)

    @staticmethod
    def _no_focus_day_response(agent_id, day=None, reason=""):
        return {
            "agent_id": agent_id,
            "day": str(day) if day else None,
            "start": None,
            "end": None,
            "booking_info": reason,
            "conflict_info": "No free blocks to reserve."
    }

    @staticmethod
    def _get_longest_continuous_free_block(free_blocks):
        longest_block = max(free_blocks, key=lambda block: sum((end - start).total_seconds() for start, end in block))
        return longest_block[0][0], longest_block[-1][1]


if __name__ == "__main__":
    service = BookingService()
    agent_id = "Luis"
    start_time = datetime(2025, 5, 24, 15, 0)
    end_time = datetime(2025, 5, 28, 17, 30)
    print(service.book_heads_down_focus_block(agent_id=agent_id,
                                              date_range_start=start_time,
                                              date_range_end=end_time,
                                              ))
