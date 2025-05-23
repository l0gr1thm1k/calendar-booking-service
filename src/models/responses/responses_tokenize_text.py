from pydantic import Field
from typing import List

from models.base_models import BaseModel
from models.examples import EXAMPLE_TOKENIZED_TEXT


class TokenizeTextResponse(BaseModel):
    tokenized_text: List[str] = Field(...,
                                      description="The tokenized text of the input text.",
                                      example=EXAMPLE_TOKENIZED_TEXT)