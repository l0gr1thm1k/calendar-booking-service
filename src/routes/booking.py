from fastapi import APIRouter
from models.requests import BookAppointmentRequest
from models.responses import BookAppointmentResponse
from structlog import get_logger

from src.calendar_booking_logic.booking_service import BookingService
from src.calendar_booking_logic.common.utils import parse_datetime
from routes.router import CustomRoute

logger = get_logger()
booking_router = APIRouter(route_class=CustomRoute)
booking_service = BookingService()


@booking_router.post('/book_appointment',
                     response_model=BookAppointmentResponse,
                     summary="Book an appointment on an agent's calendar",
                     description='This endpoint books an appointment at the requested time.')
async def post_book_appointment(payload: BookAppointmentRequest):
    """
    Book an appointment on an agent's calendar'
    """
    try:
        start_time_date= parse_datetime(payload.start_time)
    except:
        raise ValueError(f'Invalid Date time string {payload.start_time} received must be in %yyyy-%mm-%dd %HH:MM format')
    agent_name = payload.agent_id
    if agent_name not in booking_service.calendars:
        raise ValueError(f'Agent {agent_name} does not have a calendar service')
    duration = payload.duration
    appointment_title = payload.title
    booking_info = booking_service.book_appointment(agent_id=agent_name,
                                                    start_time=start_time_date,
                                                    duration_minutes=duration,
                                                    title=appointment_title)
    response = BookAppointmentResponse(agent_id=agent_name,
                                       start_time=payload.start_time,
                                       duration=duration,
                                       title=appointment_title,
                                       booking_info=booking_info['booking_info'],
                                       conflict_info=booking_info['conflict_info'])

    return response
