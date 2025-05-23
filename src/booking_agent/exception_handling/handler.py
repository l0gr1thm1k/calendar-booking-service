import traceback

from typing import Any

from booking_agent.exception_handling.exceptions import LLMChatError
from booking_agent.exception_handling.messages.loader import load_error_message
from booking_agent.logging_utils import get_logger

logger = get_logger(__name__)


def get_logged_llm_error(
    exception: Any,
    error_message_prefix: str = "chat_error"
) -> LLMChatError:
    """
    Capture and log an error traceback, return an LLMChatError with a user-friendly message.

    :param exception: The exception to log.
    :param error_message_prefix: The prefix for the error message to load.
    :return: LLMChatError with a user-friendly message.
    """
    if hasattr(exception, "__traceback__"):
        traceback_string = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    else:
        traceback_string = str(exception)

    logger.error(
        f"{error_message_prefix.upper()} | Error generating response: {exception}\nDetails:\n{traceback_string}"
    )
    user_message = load_error_message(error_message_prefix)

    return LLMChatError(user_message)
