from langchain_core.runnables import RunnableLambda
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer
import json


def get_intent_chain():
    prompt = load_prompt("intent")  # persona is injected behind the scenes
    llm = get_default_llm(tags=["intent-classification"], callbacks=[LLMTracer()])

    async def _classify(inputs: dict) -> dict:
        prompt_text = prompt.format(
            chat_history=inputs.get("chat_history", ""),
            message=inputs["message"]
        )

        result = await llm.ainvoke(prompt_text)

        try:
            parsed = json.loads(result.content)
            return parsed
        except Exception:
            return {
                "intents": ["off-topic"],
            }

    return RunnableLambda(_classify)
