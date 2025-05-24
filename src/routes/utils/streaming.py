import asyncio


from structlog import get_logger
import json
from typing import AsyncIterator, Any


logger = get_logger()


async def stream_text_from_context(
    context_manager: AsyncIterator[dict[str, Any]],
    protocol: str = 'text'
) -> AsyncIterator[str]:
    """
    Streams text or JSON protocol-compatible messages from an async context manager.

    Parameters:
    - context_manager: the async iterator yielding streaming chunks from the chain
    - protocol: either 'text' (Vercel SSE format) or 'json' (raw JSON lines)

    Yields:
    - Formatted Server-Sent Event strings for Vercel's ai-sdk, or raw JSON lines
    """
    try:
        async for step in context_manager:

            yield step

    except Exception as e:
        error_event = {"type": "error", "content": str(e)}

        yield f"data: {json.dumps(error_event)}\n\n"


async def wrap_sync_iterator(sync_iter):
    for item in sync_iter:
        yield item
        await asyncio.sleep(0)