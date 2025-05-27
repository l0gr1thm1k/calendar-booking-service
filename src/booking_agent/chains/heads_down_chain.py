from langchain_core.runnables import RunnableLambda
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer
import json
import httpx


def get_heads_down_chain():
    prompt = load_prompt("heads_down")
    llm = get_default_llm(tags=["heads down"], callbacks=[LLMTracer()])

    async def _book(inputs: dict) -> dict:
        prompt_text = prompt.format(
            message=inputs["message"],
            chat_history=inputs["chat_history"],
        )

        result = await llm.ainvoke(prompt_text)

        try:
            parsed = json.loads(result.content)

        except Exception:
            return {
                "booking_info": "We had an issue processing your request to book an appointment",
                "conflict_info": ""
            }

        heads_down_response = await book_heads_down_time(agent_name=parsed['agentId'],
                                                         start_time=parsed['startTime'],
                                                         end_time=parsed['endTime'],
                                                         )
        return heads_down_response

    return RunnableLambda(_book)


async def book_heads_down_time(agent_name, start_time, end_time) -> dict:
    payload = {
        "agentId": agent_name,
        "startTime": start_time,
        "endTime": end_time,
    }
    url = "http://localhost:7100/heads_down"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)

    response.raise_for_status()
    return response.json()
