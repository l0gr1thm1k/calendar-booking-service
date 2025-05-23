from pydantic import BaseModel


class Intent(BaseModel):
    intent: str
    output: str


class Misbehaviour(BaseModel):
    intent: str
    output: str
