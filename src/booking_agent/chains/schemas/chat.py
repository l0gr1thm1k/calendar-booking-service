from typing import List, Optional
from pydantic import BaseModel, StringConstraints, field_validator
from typing_extensions import Annotated


class ChatMessage(BaseModel):
    role: str
    content: str
    misbehavior_flag: bool = False


class ChatRequest(BaseModel):
    uuid: str
    chat_history: List[ChatMessage]


class ChatResponse(BaseModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True)]
    misbehavior_flag: bool = False

    @field_validator("text")
    def strip_prefix(cls, input_string: str) -> str:
        if input_string.startswith("Assistant :"):
            return input_string[len("Assistant :") :].strip()
        return input_string
