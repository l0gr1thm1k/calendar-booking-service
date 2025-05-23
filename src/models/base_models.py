import re

from fastapi import Body
from pydantic import BaseModel


def to_camel(s: str) -> str:
    """
    A method to convert a string to camel case
    
    :param s: an input string
    :return: a camel case string
    """
    words = re.split(r'[\s_-]+', s)
    camel_cased = words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    return camel_cased


class AsyncAPIModel(BaseModel):
    """
    Base model using orjson for (de)serialization
    """

    class Config:
        # Forbid extra model parameters
        extra = 'forbid'
        # Don't force use of aliases in class instantiation/attribute access
        populate_by_name = True
        # Convert snake_case to camelCase
        alias_generator = to_camel


class ErrorResponse(AsyncAPIModel):
    """
    Response model for errors
    """

    message: str = Body(None, alias='message', description='Error message',
                        example='Unhandled exception in application')