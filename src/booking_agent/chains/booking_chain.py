from langchain_core.runnables import RunnableLambda
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer
import json
import httpx


def get_booking_chain():
    prompt = load_prompt("booking")
    llm = get_default_llm(tags=["booking"], callbacks=[LLMTracer()])

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

        booking_response = await book_appointment(agent_name=parsed['agent_name'],
                                                  start_time=parsed['start_time'],
                                                  duration=parsed['duration_minutes'],
                                                  title=parsed['title'],
                                                  )
        return booking_response

    return RunnableLambda(_book)


async def book_appointment(agent_name, start_time, title, duration=30) -> dict:
    payload = {
        "agentId": agent_name,
        "startTime": start_time,
        "duration": duration,
        "title": title
    }
    url = "http://localhost:7100/book_appointment"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)

    response.raise_for_status()
    return response.json()
