from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import pytz
from ics import Calendar

from calendar_booking_logic.common.constants import DATA_DIR, FRONTEND_DIR


def create_workday_schedule_plot(file_path: str, start_date: datetime, num_days: int = 7):
    tz = pytz.timezone("US/Pacific")
    with open(file_path, "r") as f:
        calendar = Calendar(f.read())

    full_day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    active_days = full_day_labels[:num_days]
    events = []

    for event in calendar.events:
        start = event.begin.astimezone(tz).replace(tzinfo=None)
        end = event.end.astimezone(tz).replace(tzinfo=None)

        # Skip events outside workday
        if end.hour < 9 or start.hour >= 17:
            continue

        # Clamp to workday boundaries
        start_decimal = max(9, start.hour + start.minute / 60)
        end_decimal = min(17, end.hour + end.minute / 60)

        day_index = start.weekday()
        if day_index >= num_days:
            continue

        events.append({
            "name": event.name,
            "start": start,
            "end": end,
            "day": full_day_labels[day_index],
            "start_decimal": start_decimal,
            "end_decimal": end_decimal,
        })

    fig = go.Figure()

    for event in events:
        fig.add_trace(go.Bar(
            x=[event["day"]],
            y=[event["end_decimal"] - event["start_decimal"]],
            base=event["start_decimal"],
            name=event["name"],
            orientation='v',
            marker=dict(color='tomato' if "Busy" in event["name"] else 'lightgray'),
            width=0.7,
            hovertemplate=f"{event['name']}<br>{event['start'].strftime('%H:%M')}–{event['end'].strftime('%H:%M')}"
        ))

    fig.update_layout(
        title="Week Calendar View (9AM–5PM)",
        barmode='overlay',
        yaxis=dict(title='Time of Day', autorange='reversed', range=[17, 9], tickvals=list(range(9, 18))),
        xaxis=dict(
            title='Day of Week',
            categoryorder='array',
            categoryarray=active_days,
        ),
        height=600,
        margin=dict(l=60, r=60, t=60, b=60),
        showlegend=False
    )
    output_path_html = str(Path(FRONTEND_DIR) / "weekly_calendar.html")

    fig.write_html(output_path_html, include_plotlyjs="cdn")


if __name__ == "__main__":
    name = "Luis"
    cal_start_date = datetime.today()
    create_workday_schedule_plot(str(Path(DATA_DIR) / f"agent_{name}.ics"),
                                 start_date=cal_start_date,
                                 num_days=7)
