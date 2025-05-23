from pydantic import Field


from models.base_models import BaseModel
from models.examples import (EXAMPLE_AGENT, EXAMPLE_START_TIME, EXAMPLE_DURATION, EXAMPLE_TITLE, EXAMPLE_BOOKING_INFO,
                             EXAMPLE_CONFLICT_INFO)


class BookAppointmentResponse(BaseModel):
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
    booking_info: str = Field(...,
                              description="Information about the booked appointment",
                              example=EXAMPLE_BOOKING_INFO)
    conflict_info: str = Field(...,
                               description="Information about the conflict of the booked appointment",
                               example=EXAMPLE_CONFLICT_INFO)
