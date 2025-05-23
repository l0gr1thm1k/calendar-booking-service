from pydantic import Field

from models.base_models import AsyncAPIModel
from models.examples import EXAMPLE_AGENT, EXAMPLE_START_TIME, EXAMPLE_DURATION, EXAMPLE_TITLE


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
    