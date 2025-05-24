from langchain_core.runnables import RunnableLambda
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer


def get_summarize_chain() -> RunnableLambda:
    prompt = load_prompt("summarize")
    llm = get_default_llm(tags=["summarize-question"], callbacks=[LLMTracer()])

    async def _summarize(inputs: dict) -> dict:
        prompt_text = prompt.format(
            chat_history=inputs.get("chat_history", ""),
            message=inputs["message"]
        )
        result = await llm.ainvoke(prompt_text)
        return {"summary": result.content.strip()}

    return RunnableLambda(_summarize)
