import asyncio

from langchain_core.runnables import RunnableLambda, RunnableParallel
from booking_agent.chains.intent import get_intent_chain
from booking_agent.chains.misbehavior import get_misbehavior_chain
from booking_agent.chains.response_generator import get_streaming_response_chain
from booking_agent.chains.summarize_question import get_summarize_chain
from booking_agent.chains.booking_chain import get_booking_chain
from booking_agent.chains.availability_chain import get_availability_chain
from booking_agent.chains.heads_down_chain import get_heads_down_chain
from booking_agent.logging_utils import get_logger

from calendar_booking_logic.common.utils import to_pdt
from datetime import datetime
from collections import defaultdict


logger = get_logger(__name__)


def get_booking_agent_chain() -> RunnableLambda:
    """
    1. Check for misbehavior / unsafe input
    2. Classify the user’s intent: book / availability.txt / heads down
    3. If book:
       → Run book appointment
    4. If availability.txt request:
       → Run availability.txt
    5. If heads down
       → Block off time on available day
    6. Return combined response

    :param request:
    :return:
    """
    intent_chain = get_intent_chain()
    misbehavior_chain = get_misbehavior_chain()
    summarize_chain = get_summarize_chain()
    response_chain = get_streaming_response_chain()

    booking_chain = get_booking_chain()
    availability_chain = get_availability_chain()
    heads_down_chain = get_heads_down_chain()

    async def _run(inputs: dict) -> dict:
        message = inputs["message"]
        chat_history = inputs.get("chat_history", "")
        logger.info(f"Chain received message: {message}")

        parallel = RunnableParallel(
            intent=intent_chain,
            misbehavior=misbehavior_chain,
            summary=summarize_chain
        )
        results = await parallel.ainvoke({
            "message": message,
            "chat_history": chat_history
        })

        intents = results["intent"].get("intents", [])
        misbehavior = results["misbehavior"]
        summary = results["summary"]

        if misbehavior == "unsafe":
            async for chunk in stream_text_response(
                    "That seems outside the realm of scheduling meetings for you via HouseWhisper. I'm best at helping you manage your schedule"
            ):
                yield chunk

            return

        # Step 2: Short-circuit if off-topic
        if intents == ["off-topic"]:
            async for chunk in stream_text_response("That seems outside the realm of scheduling meetings for you via HouseWhisper. I'm best at helping you manage your schedule"
                                                    ):
                yield chunk

            return

        logger.info(f"Intents identified: {intents}")
        # Step 3: Prepare and run context chains
        chains_to_run = {}
        if 'book' in intents:
            chains_to_run["book"] = booking_chain.ainvoke({"message": message})

        if 'availability' in intents:
            chains_to_run["availability"] = availability_chain.ainvoke({"message": message})

        if 'heads down' in intents:
            chains_to_run["heads down"] = heads_down_chain.ainvoke({"message": message})

        context = {
        }
        if chains_to_run:
            chain_results = await asyncio.gather(*chains_to_run.values())
            context = dict(zip(chains_to_run.keys(), chain_results))
        if 'book' in context:
            booking_context = "/n".join([context['book']['booking_info'], context['book']['conflict_info']])
        else:
            booking_context = ''

        if 'availability' in context:
            # availability_context = [str(slot) for slot in context['availability']['available_slots']]
            availability_context = format_available_slots(context['availability']['available_slots'])
        else:
            availability_context = ''

        if 'heads down' in context:
            heads_down_context = "/n".join([context['heads down']['booking_info'], context['heads down']['conflict_info']])
        else:
            heads_down_context = ''

        # Step 4: Prepare final generation input
        response_input = {
            "chat_history": chat_history,
            "message": message,
            "summary": summary,
            "intents": intents,
            "booking_context": booking_context,
            "availability_context": availability_context,
            "heads_down_context": heads_down_context,
        }

        async for chunk in response_chain.astream(response_input):
            print(chunk, end='', flush=True)
            yield chunk
        print("\n")

    return RunnableLambda(_run)


def format_available_slots(slots):
    grouped_by_date = defaultdict(list)

    for slot in slots:
        start_dt = datetime.fromisoformat(slot["start"])
        end_dt = datetime.fromisoformat(slot["end"])
        local_start = to_pdt(start_dt)
        local_end = to_pdt(end_dt)

        date_str = local_start.strftime("%A, %B %d")
        time_str = f"{local_start.strftime('%-I:%M %p')} – {local_end.strftime('%-I:%M %p')}"
        grouped_by_date[date_str].append(time_str)

    # Build the response string
    formatted = []
    for date, times in grouped_by_date.items():
        formatted.append(f"Available time slots on {date}:")
        for t in times:
            formatted.append(f"- {t}")
    return "\n".join(formatted)


async def stream_text_response(text: str):
    for ch in text:
        yield ch
        await asyncio.sleep(0.01)


if __name__ == '__main__':
    chain = get_booking_agent_chain()
    payload = {"message": "Schedule me focus time on Tuesday",
               "messages": []}
    resp = asyncio.run(chain.ainvoke(payload))