from pydantic import Field

from models.base_models import AsyncAPIModel
from models.examples import (EXAMPLE_AGENT, EXAMPLE_START_TIME, EXAMPLE_DURATION, EXAMPLE_TITLE, EXAMPLE_END_TIME,
                             EXAMPLE_NUMBER_OF_SLOTS)


class BookAppointmentRequest(AsyncAPIModel):
    """
    Request model for the POST /tokenize_text endpoint
    """
    agent_id: str = Field(...,
                          description="The agent's name",
                          example=EXAMPLE_AGENT)
    start_time: str = Field(...,
                            description="The start time of the appointment",
                            example=EXAMPLE_START_TIME)
    duration: int = Field(...,
                          description="The event duration in minutes",
                          example=EXAMPLE_DURATION)
    title: str = Field(...,
                       description="The name of the appointment to book",
                       example=EXAMPLE_TITLE)


class AvailabilityRequest(AsyncAPIModel):
    """
    Request model for finding available appointment times
    """
    agent_id: str = Field(...,
                          description="The agent's name",
                          example=EXAMPLE_AGENT)
    start_time: str = Field(...,
                            description="The start of the availability window",
                            example=EXAMPLE_START_TIME)
    end_time: str = Field(...,
                          description="The end of the availability window",
                          example=EXAMPLE_END_TIME)
    duration: int = Field(...,
                          description="Minimum duration of availability in minutes",
                          example=EXAMPLE_DURATION)
    max_slots: int = Field(5,
                           description="Maximum number of available slots to return",
                           example=EXAMPLE_NUMBER_OF_SLOTS)


class HeadsDownRequest(AsyncAPIModel):
    """
    Request model for the POST /heads_down endpoint
    """
    agent_id: str = Field(...,
                          description="The agent's name",
                          example=EXAMPLE_AGENT)
    start_time: str = Field(...,
                            description="The start time of the window for scheduling heads down time",
                            example=EXAMPLE_START_TIME)
    end_time: str = Field(...,
                          description="The end time of the window for scheduling heads down time",
                          example=EXAMPLE_END_TIME)