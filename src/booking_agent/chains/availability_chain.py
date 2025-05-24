from langchain_core.runnables import RunnableLambda
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer
import json
import httpx

from booking_agent.common.constants import DEFAULT_AGENT_IDENTIFIER


def get_availability_chain():
    prompt = load_prompt("availability")
    llm = get_default_llm(tags=["availability"], callbacks=[LLMTracer()])

    async def _availability(inputs: dict) -> dict:
        prompt_text = prompt.format(
            message=inputs["message"]
        )

        result = await llm.ainvoke(prompt_text)

        try:
            parsed = json.loads(result.content)

        except Exception:
            return {
                "agent_id": DEFAULT_AGENT_IDENTIFIER,
                "available_slots": [],
                "availability_info": "There were no times available in the target range"
            }

        availability_response = await get_availability(agent_name=parsed['agentId'],
                                                       start_time=parsed['startTime'],
                                                       end_time=parsed['endTime'],
                                                       duration=parsed['duration'],
                                                       max_slots=parsed['maxSlots'])

        return availability_response

    return RunnableLambda(_availability)


async def get_availability(agent_name, start_time, end_time, duration=30, max_slots=5) -> dict:
    payload = {
        "agentId": agent_name,
        "startTime": start_time,
        "endTime": end_time,
        "duration": duration,
        "maxSlots": max_slots,
    }
    url = "http://localhost:7100/availability"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)

    response.raise_for_status()
    return response.json()
