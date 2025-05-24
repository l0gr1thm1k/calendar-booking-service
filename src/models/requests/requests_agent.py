from pydantic import Field
from typing import List, Optional
from pydantic import BaseModel

from models.base_models import AsyncAPIModel
from models.examples import EXAMPLE_UUID, EXAMPLE_CHAT_HISTORY


class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str


class ToolInvocation(BaseModel):
    toolCallId: str
    toolName: str
    args: dict
    result: dict


class ClientMessage(BaseModel):
    role: str
    content: str
    #experimental_attachments: Optional[List[ClientAttachment]] = None
    #toolInvocations: Optional[List[ToolInvocation]] = None


class ChatRequest(AsyncAPIModel):
    messages: List[ClientMessage] = Field(..., description="List of messages in the chat history",
                                          example=EXAMPLE_CHAT_HISTORY)
    id: Optional[str] = Field(...,
                              description="Unique identifier for the chat session",
                              example=EXAMPLE_UUID)
