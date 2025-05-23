from time import time
from typing import Any, Dict, List, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from booking_agent.logging_utils import get_logger

logger = get_logger(__name__)


class LLMTracer(BaseCallbackHandler):
    """LangChain callback that logs LLM input/output events."""

    def __init__(self):
        self._in_progress_llm_runs = {}

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> Any:
        run_id = str(kwargs["run_id"])
        request_id = str(kwargs.get("metadata", {}).get("request_id", "unknown"))
        self._in_progress_llm_runs[run_id] = {
            "serialized": serialized,
            "prompts": prompts,
            "request_id": request_id,
            **kwargs,
        }
        self._start = time()

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        run_id = str(kwargs["run_id"])
        self._in_progress_llm_runs[run_id] |= {
            "response": response,
            **kwargs,
        }
        self._end = time()
        self._log_run(run_id, success=True)

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> Any:
        run_id = str(kwargs["run_id"])
        self._in_progress_llm_runs[run_id] |= {
            "error": error,
            **kwargs,
        }
        self._log_run(run_id, success=False)

    def _log_run(self, run_id: str, success: bool):
        data = self._in_progress_llm_runs.pop(run_id)
        latency = self._end - self._start if hasattr(self, "_end") else None
        logger.info(
            f"LLM Run {'✅ Success' if success else '❌ Error'} | Request ID: {data.get('request_id')} | "
            f"Prompts: {data.get('prompts')} | Latency: {latency:.3f}s"
        )
