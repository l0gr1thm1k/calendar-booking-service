# Calendar Booking Service


## Setup Test Data

### a. Calendar Generation
This project uses ICS calendar files (.ics) to simulate agent availability. The included helper function create_randomized_week_calendar generates synthetic weekly calendars for individual agents.

Each agent’s calendar is structured as follows:

Busy time from 12:00 AM to 9:00 AM and from 5:00 PM to 11:59 PM to reflect typical non-working hours.

0 to 8 hours of randomly scheduled busy time between 9 AM and 5 PM, simulating variability in daily workloads.

Remaining hours within the 9–5 window are considered available.

Calendars are saved under the `src/calendar_booking_logic/data/` directory (note the directory is created on the fly when the service starts). A visualization function, `visualize_workday_schedule`, renders a color-coded matplotlib chart for quick analysis of busy vs. free time blocks.

### b. Purpose of Test Data
This test data is designed to simulate realistic and diverse agent schedules, enabling end-to-end validation of key features, including:

Availability querying: Determining when an agent is free given dynamic and partially booked calendars.

Appointment booking: Verifying that new events are scheduled only during free time.

Workload recommendations: Identifying underutilized days where additional work could be scheduled.

The variation in scheduled hours (from 0 to 8) helps validate edge cases such as fully booked, mostly free, and mixed-availability days.


## API Features
The API itself uses a boilerplate project I wrote for building a REST API microservice. This template provides a simple, scalable foundation for developing RESTful APIs, with built-in features like dependency management, structured logging, and environment-based configuration.

- **FastAPI** framework for handling RESTful endpoints
- **Poetry** for dependency management
- **Docker** support for containerized deployment
- Environment-based configuration management
- Structured logging
- Automated testing with **Pytest**

## Prerequisites

- **Python 3.x**: Ensure Python is installed on your system.
- **Poetry**: Used for dependency management.
  ```bash
  pip install poetry
  
### Dependencies
Once Python and poetry are installed, you can install the project dependencies by doing the following in a terminal

```bash 
poetry config virtualenvs.create false
poetry install
```

## Usage
### Running the Application
To start the application locally:

```bash 
python application.py
```
The API will be available at http://127.0.0.1:7100/ui.

### Running with Docker
If you prefer to use Docker, build and run the container:

```bash
docker build -t rest-api-template .
docker run -d -p 7100:7100 rest-api-template
```

### API Endpoints
You will create your own endpoints, but some common endpoint types that are REST are listed below.

* GET: Retrieve a resource.
* POST: Insertion of a datapoint or other API action.
* PUT: Initial creation of a resource or item.
* DELETE: Delete an item.

Here is in depth [documentation](https://docs.github.com/en/rest?apiVersion=2022-11-28) around REST if you would like to read further.

### Testing
To run the test suite:

```bash 
pytest
```

### General Application Structure
bash
```
├── src
│   ├── application.py           # Application entry point
|   ├── prometheus_middleware.py # Application middleware
│   ├── routes                   # API route definitions
│   ├── models                   # API data models
|   |   ├── requests             # Data models going into the system
|   |   └── responses            # Data models going out of the system
├── Dockerfile                   # Project Dockerfile
├── docker-compose.yml           # Project docker compose, can combine multiple services
├── pyproject.toml               # Poetry dependency configuration
└── README.md                    # Project documentation
```

## Front End

A streamlit app based off the open source work done here https://github.com/SaiAkhil066/DeepSeek-RAG-Chatbot