from langchain_core.runnables import RunnableLambda
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer


def get_misbehavior_chain():
    prompt = load_prompt("misbehavior")
    llm = get_default_llm(tags=["misbehavior-check"], callbacks=[LLMTracer()])

    async def _classify(inputs: dict) -> dict:
        prompt_text = prompt.format(
            chat_history=inputs.get("chat_history", ""),
            message=inputs["message"]
        )
        result = await llm.ainvoke(prompt_text)
        return {"misbehavior": result.content.strip().lower()}

    return RunnableLambda(_classify)
