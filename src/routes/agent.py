from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from structlog import get_logger

from models.requests import ChatRequest
from booking_agent.chains.booking_agent_chain import get_booking_agent_chain
from routes.router import CustomRoute
from routes.utils.streaming import stream_text_from_context

chain = get_booking_agent_chain()
logger = get_logger()
agent_router = APIRouter(route_class=CustomRoute)


@agent_router.post("/stream")
async def post_stream(request: ChatRequest, protocol: str = Query('text')):
    message = request.messages[-1].content
    message_history = [msg.content for msg in request.messages[:-1]]
    context_manager = chain.astream({"message": message,
                                     "chat_history": message_history})
    response = StreamingResponse(stream_text_from_context(context_manager, protocol=protocol))
    response.headers['x-vercel-ai-data-stream'] = 'v1'

    return response
