from fastapi import APIRouter
from models.requests import TokenizeTextRequest
from models.responses import TokenizeTextResponse
from structlog import get_logger

from application_logic.example_application_logic import tokenize_text  
from routes.router import CustomRoute

logger = get_logger()
booking_router = APIRouter(route_class=CustomRoute)


@booking_router.post('/tokenize_text',
                         response_model=TokenizeTextResponse,
                         summary='Tokenize an input string splitting tokens on white space.',
                         description='This is an example endpoint that does a simple tokenize operation.')
async def post_tokenize_text(payload: TokenizeTextRequest):
    """
    Tokenize an input string.
    
    :param payload: The input string to tokenize 
    :return: The tokenized input as a list of strings.
    """
    string_to_tokenize = payload.text
    tokenized_text = tokenize_text(string_to_tokenize)
    response = TokenizeTextResponse(tokenized_text=tokenized_text)

    return response