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


class HeadsDownResponse(BaseModel):
    agent_id: str = Field(...,
                          description="The agent's name",
                          example=EXAMPLE_AGENT)
    day: str = Field(...,
                     description="The day selected for heads-down focus time (YYYY-MM-DD)",
                     example="2025-05-25")
    start: str = Field(...,
                       description="Start time of the focus block",
                       example=EXAMPLE_START_TIME)
    end: str = Field(...,
                     description="End time of the focus block",
                     example=EXAMPLE_END_TIME)
    booking_info: str = Field(...,
                              description="Details about the Focus Time event booking",
                              example="Focus Time booked from 09:00 to 15:00 on 2025-05-25 covering 6.0 hours of uninterrupted time.")
    conflict_info: str = Field(...,
                               description="Summary of how many other meetings occurred on the selected day or other conflict information",
                               example="1 other meetings were found on this day.")