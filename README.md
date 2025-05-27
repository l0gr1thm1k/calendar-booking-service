# Calendar Booking Service

This is a demo system for exploring calendar booking using RESTful APIs, a LangChain agent service, and a real-time chat UI.

## Usage

### Prerequisites

- **Docker**
- a `.env` file placed in the projects top level directory with the following fields

```
OPENAI_API_KEY=your-open-ai-key-here
DEFAULT_OPENAI_MODEL=gpt-4o-mini
DEFAULT_AGENT_IDENTIFIER=Luis
```

### Run Locally

```bash
docker-compose up --build
```

Access the API at: [http://0.0.0.0:7100/ui](http://0.0.0.0:7100/ui)

Access the streamlit frontend at [http://0.0.0.0:8501/](http://0.0.0.0:8501/)

---

## 1. Data

### a. Calendar Generation

This project uses ICS calendar files (.ics) to simulate agent availability. The included helper function `create_randomized_week_calendar` generates synthetic weekly calendars for individual agents.

Each agent’s calendar is structured as follows:

- Busy time from 12:00 AM to 9:00 AM and from 5:00 PM to 11:59 PM to reflect typical non-working hours.
- 0 to 8 hours of randomly scheduled busy time between 9 AM and 5 PM, simulating variability in daily workloads.
- Remaining hours within the 9–5 window are considered available.

Calendars are saved under the `src/calendar_booking_logic/data/` directory (note the directory is created on the fly when the service starts). A visualization function, `visualize_workday_schedule`, renders a color-coded matplotlib chart for quick analysis of busy vs. free time blocks.

### b. Purpose of Test Data

This test data is designed to simulate realistic and diverse agent schedules, enabling end-to-end validation of key features, including:

- **Availability querying**: Determining when an agent is free given dynamic and partially booked calendars.
- **Appointment booking**: Verifying that new events are scheduled only during free time.
- **Workload recommendations**: Identifying underutilized days where additional work could be scheduled.

The variation in scheduled hours (from 0 to 8) helps validate edge cases such as fully booked, mostly free, and mixed-availability days.

---

## 2. REST Service

A core component of the system is a FastAPI-based REST service that manages all agent calendars. On startup, randomized weekly calendars are generated and stored in memory by agent name. All endpoints interact with these calendars.

### Endpoints

#### `POST /book_appointment`

Books a meeting on the specified agent's calendar regardless of existing events.

```json
{
  "agentId": "Luis",
  "startTime": "2025-05-28 10:30 AM",
  "duration": 60,
  "title": "Calendar Booking Service Demo"
}
```

Response format:

```json 
{
  "agent_id": "Luis",
  "start_time": "2025-05-28 10:30 AM",
  "duration": 60,
  "title": "Calendar Booking Service Demo",
  "booking_info": "New Calendar event 'Calendar Booking Service Demo' for agent 'Luis' created.",
  "conflict_info": "Conflict detected with event: Luis - Busy Block at 2025-05-28 11:00:00-07:00–2025-05-28 11:30:00-07:00"
}
```

#### `POST /availability`

Returns available time slots of a given duration within a specific time range.

```json
{
  "agentId": "Luis",
  "startTime": "2025-05-28 10:30 AM",
  "endTime": "2025-05-31 5:00 PM",
  "duration": 60,
  "maxSlots": 5
}
```

Response format:

```json
[
  {
    "start": "2025-05-28T13:00:00-07:00",
    "end": "2025-05-28T14:00:00-07:00"
  }
]
```

#### `POST /heads_down`

Identifies the day with the most available time within a given date range and books a "Focus Time" block.

```json
{
  "agentId": "Luis",
  "startTime": "2025-05-27 9:00 AM",
  "endTime": "2025-05-31 5:00 PM",
  "duration": 180
}
```

Response format:

```json
{
  "agent_id": "Luis",
  "day": "2025-05-29",
  "start": "2025-05-29T10:00:00-07:00",
  "end": "2025-05-29T13:00:00-07:00",
  "booking_info": "Focus Time booked from 10:00 to 13:00 on 2025-05-29 covering 3.0 hours of uninterrupted time.",
  "conflict_info": "1 other meetings were found on this day."
}
```

---

## 3. Agent Service (LLM Interface)

This component wraps the booking service with a conversational interface powered by LangChain and API calls to OpenAI.

### Workflow

1. **Safety Check**  
   Messages are first screened for inappropriate or malicious content.

2. **Intent Classification**  
   Determines what the user wants based on the message and prior chat history. Supported intents:
   - `off-topic`
   - `book`
   - `availability`
   - `heads_down`

3. **Summarization**  
   Maintains continuity across turns by summarizing the conversation (e.g., understanding "book the 11am slot" in the context of prior availability queries).

4. **Execution**  
   Intent-specific LangChain chains convert user input into structured API calls to the REST service.

5. **Response Generation**  
   A final chain generates a natural language reply based on all actions taken and context gathered.

---

## 4. Front-End

Built with Streamlit, the front end provides an interactive chat interface based on [this open source repo](https://github.com/SaiAkhil066/DeepSeek-RAG-Chatbot).

### Enhancements

- **Streaming Responses**: Integrated backend streaming support to allow fluid LLM interaction.
- **Visual Calendar Previews**: Shows a rendered calendar image during chat to help users confirm the agent’s actions are working as expected.

---

## 5. Design Notes

- **Dynamic Calendar Generation** on startup; supports stateless architecture and simplified testing.
- **No Conflict Checking** for bookings at the API level — downstream tools (like the agent) handle conflicts.
- **OpenAI API Integration** ensures high-quality LLM behavior without local compute dependencies.
- **LangChain Abstractions** cleanly separate intents, making it easy to extend or modify.
- **Context Preservation** via summarization supports follow-up instructions and multi-turn coherence.
- **Portability Focus**: All components run without heavy local hardware requirements, making this demo easy to share and deploy.

---



