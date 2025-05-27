from datetime import datetime, timedelta
from pathlib import Path

import plotly.graph_objects as go
import pytz
from ics import Calendar

from calendar_booking_logic.common.constants import DATA_DIR, SHARED_MOUNT_DIR


def create_workday_schedule_plot(file_path: str, start_date: datetime, num_days: int = 7):
    tz = pytz.timezone("US/Pacific")
    with open(file_path, "r") as f:
        calendar = Calendar(f.read())

    # Generate day labels starting from start_date
    day_dates = [(start_date + timedelta(days=i)) for i in range(num_days)]
    active_day_labels = [d.strftime("%a %m/%d") for d in day_dates]

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

        # Only include events within the active date range
        event_date_label = start.strftime("%a %m/%d")
        if event_date_label not in active_day_labels:
            continue

        events.append({
            "name": event.name,
            "start": start,
            "end": end,
            "day": event_date_label,
            "start_decimal": start_decimal,
            "end_decimal": end_decimal,
        })

    fig = go.Figure()

    for event in events:
        if 'Busy' in event['name']:
            color = 'tomato'
        elif 'Focus Time' in event['name']:
            color = 'lightgreen'
        else:
            color = 'lightblue'
        fig.add_trace(go.Bar(
            x=[event["day"]],
            y=[event["end_decimal"] - event["start_decimal"]],
            base=event["start_decimal"],
            name=event["name"],
            orientation='v',
            marker=dict(color=color),
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
            categoryarray=active_day_labels,
        ),
        height=600,
        margin=dict(l=60, r=60, t=60, b=60),
        showlegend=False
    )

    output_path_html = str(Path(SHARED_MOUNT_DIR) / "weekly_calendar.html")
    fig.write_html(output_path_html, include_plotlyjs="cdn")


if __name__ == "__main__":
    name = "Luis"
    cal_start_date = datetime.today()
    create_workday_schedule_plot(str(Path(DATA_DIR) / f"agent_{name}.ics"),
                                 start_date=cal_start_date,
                                 num_days=7)
