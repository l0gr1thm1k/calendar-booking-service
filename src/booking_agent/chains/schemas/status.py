from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "OK"


class LogResponse(BaseModel):
    response: str
