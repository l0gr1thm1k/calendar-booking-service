from pydantic import Field

from models.base_models import AsyncAPIModel
from models.examples import EXAMPLE_TEXT


class TokenizeTextRequest(AsyncAPIModel):
    """
    Request model for the POST /tokenize_text endpoint
    """
    text : str = Field(...,
                       description="Text to tokenize",
                       example=EXAMPLE_TEXT)
    