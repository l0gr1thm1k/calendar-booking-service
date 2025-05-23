from langchain_openai import ChatOpenAI
from booking_agent.llm_tracing.tracer import LLMTracer
from booking_agent.common.constants import (
    OPENAI_API_KEY,
    DEFAULT_OPENAI_MODEL,
)


def get_default_llm(*, tags=None, callbacks=None, **overrides) -> ChatOpenAI:
    return ChatOpenAI(
        model_name=DEFAULT_OPENAI_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.1,
        max_tokens=512,
        callbacks=callbacks or [LLMTracer()],
        tags=tags or ["langchain"],
        **overrides,
    )


if __name__ == '__main__':
    llm = get_default_llm()
    response = llm.invoke("What is HouseWhisper, and why is it awesome?")
    print(response)