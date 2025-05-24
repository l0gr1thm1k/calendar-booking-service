from pydantic import Field
from typing import List

from models.base_models import BaseModel
from models.examples import (EXAMPLE_AGENT, EXAMPLE_START_TIME, EXAMPLE_DURATION, EXAMPLE_TITLE, EXAMPLE_BOOKING_INFO,
                             EXAMPLE_CONFLICT_INFO, EXAMPLE_END_TIME, EXAMPLE_AVAILABLE_SLOTS)


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


class AvailabilitySlot(BaseModel):
    start: str = Field(...,
                       description="The start time of the available slot",
                       example=EXAMPLE_START_TIME)
    end: str = Field(...,
                     description="The end time of the available slot",
                     example=EXAMPLE_END_TIME)


class AvailabilityResponse(BaseModel):
    agent_id: str = Field(...,
                          description="The agent's name",
                          example=EXAMPLE_AGENT)
    available_slots: List[AvailabilitySlot] = Field(...,
                                                    description="List of available time slots for the agent",
                                                    example=EXAMPLE_AVAILABLE_SLOTS)