from ics import Calendar, Event
from datetime import datetime, timedelta

import pytz
import matplotlib.pyplot as plt
from calendar_booking_logic.common.constants import DATA_DIR
from pathlib import Path


def visualize_workday_schedule(file_path: str, start_date: datetime, num_days: int):
    tz = pytz.timezone("US/Pacific")
    work_start = 9
    work_end = 17

    with open(file_path, "r") as f:
        calendar = Calendar(f.read())

    days = []
    schedules = []

    for day_offset in range(num_days):
        day = start_date + timedelta(days=day_offset)
        day_start = tz.localize(datetime(day.year, day.month, day.day, work_start))
        day_end = tz.localize(datetime(day.year, day.month, day.day, work_end))

        # Initialize all slots as free
        schedule = [(day_start + timedelta(minutes=30 * i), False) for i in range((work_end - work_start) * 2)]

        for event in calendar.events:
            if event.begin.date() != day.date():
                continue
            for i, (slot_start, _) in enumerate(schedule):
                slot_end = slot_start + timedelta(minutes=30)
                if event.begin < slot_end and event.end > slot_start:
                    schedule[i] = (slot_start, True)

        days.append(day.strftime("%a %m-%d"))
        schedules.append(schedule)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 0.6 * num_days))
    for i, (day_label, schedule) in enumerate(zip(days, schedules)):
        for start_time, is_busy in schedule:
            color = 'red' if is_busy else 'green'
            ax.barh(
                y=i,
                width=0.5,
                left=(start_time.hour + start_time.minute / 60),
                height=0.8,
                color=color,
                edgecolor='black'
            )
    ax.set_yticks(range(len(days)))
    ax.set_yticklabels(days)
    ax.set_xlim(work_start, work_end)
    ax.set_xlabel("Hour of Day")
    ax.set_title("Daily Schedule: Busy (Red) vs Free (Green)")
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    name = "Luis"
    start_date = datetime.today()
    visualize_workday_schedule(str(Path(DATA_DIR) / f"agent_{name}.ics"),
                               start_date=start_date,
                               num_days=7)
