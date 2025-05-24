from pydantic import Field
from typing import List

from models.base_models import BaseModel

from models.examples import EXAMPLE_CONTENT


class ChatResponse(BaseModel):
    status_code: int = Field(...,
                             description="request status code",
                             example=200)
    type: str = Field(...,
                      description="type of response",
                      example="assistant_response")
    response: str = Field(...,
                          description="response from the assistant",
                          example="I've scheduled Tea at 12:00 PM Wednesday the 28th of May")
    intents: List[str] = Field(...,
                                description="intents identified in the response",
                                example=["book"])
    chat_history: List[str] = Field(...,
                                    description="chat history",
                                    example=[EXAMPLE_CONTENT])
    summary: str = Field(...,
                         description="summary of the message and the chat history",
                         example="The agent wants to schedule an appointment 'Tea' at '2025-05-28 12:00 PM' for 30 minutes"
                         )
