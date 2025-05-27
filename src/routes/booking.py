from fastapi import APIRouter
from models.requests import AvailabilityRequest, BookAppointmentRequest, HeadsDownRequest
from models.responses import AvailabilityResponse, AvailabilitySlot, BookAppointmentResponse, HeadsDownResponse
from structlog import get_logger

from calendar_booking_logic.booking_service import BookingService
from calendar_booking_logic.common.utils import parse_datetime
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


@booking_router.post('/availability',
                     response_model=AvailabilityResponse,
                     summary="Find available time slots on the agent's calendar",
                     description="Get time slot availability on the agents calendar")
async def post_availability(payload: AvailabilityRequest):
    try:
        start_time_date = parse_datetime(payload.start_time)
    except:
        raise ValueError(f"Invalid start date time string {payload.start_time}")
    try:
        end_time_date = parse_datetime(payload.end_time)
    except:
        raise ValueError(f"Invalid end date time string {payload.end_time}")

    agent = payload.agent_id
    duration = payload.duration
    slots = payload.max_slots

    availability = booking_service.find_available_times(agent_id=agent,
                                                        date_range_start=start_time_date,
                                                        date_range_end=end_time_date,
                                                        duration_minutes=duration,
                                                        max_slots=slots)
    list_of_slot_objects = [AvailabilitySlot(start=slot['start'], end=slot['end']) for slot in availability]

    response = AvailabilityResponse(agent_id=agent,
                                    available_slots=list_of_slot_objects)

    return response


@booking_router.post('/heads_down',
                     response_model=HeadsDownResponse,
                     summary="book a day of heads down focus time",
                     description="find the day within the specified parameters and book focus time on your calendar")
async def post_heads_down(payload: HeadsDownRequest):
    try:
        start_time_date = parse_datetime(payload.start_time)
    except:
        raise ValueError(f"Invalid start date time string {payload.start_time}")
    try:
        end_time_date = parse_datetime(payload.end_time)
    except:
        raise ValueError(f"Invalid end date time string {payload.end_time}")

    agent = payload.agent_id
    response = booking_service.book_heads_down_focus_block(agent_id=agent,
                                                           date_range_start=start_time_date,
                                                           date_range_end=end_time_date)

    return HeadsDownResponse(agent_id=agent,
                             day=response['day'],
                             start=response['start'],
                             end=response['end'],
                             booking_info=response['booking_info'],
                             conflict_info=response['conflict_info'])


@booking_router.get('/randomize_calendars')
def get_randomize_calendars():
    booking_service._generate_new_calendars()

    return {"message": "Calendars randomized"}