import asyncio

from langchain_core.runnables import RunnableLambda, RunnableParallel
from booking_agent.chains.intent import get_intent_chain
from booking_agent.chains.misbehavior import get_misbehavior_chain
from booking_agent.chains.response_generator import get_response_chain
from booking_agent.chains.summarize_question import get_summarize_chain
from booking_agent.logging_utils import get_logger


logger = get_logger(__name__)


def get_booking_agent_chain() -> RunnableLambda:
    """
    1. Check for misbehavior / unsafe input
    2. Classify the user’s intent: book / availability / heads down
    3. If book:
       → Run book appointment
    4. If availability request:
       → Run availability
    5. If heads down
       → Block off time on available day
    6. Return combined response

    :param request:
    :return:
    """
    intent_chain = get_intent_chain()
    misbehavior_chain = get_misbehavior_chain()
    summarize_chain = get_summarize_chain()
    response_chain = get_response_chain()

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
            return {
                "type": "misbehavior_block",
                "error": "Input flagged as unsafe."
            }

        # Step 2: Short-circuit if off-topic
        if intents == ["off-topic"]:
            return {
                "type": "off_topic",
                "response": "That seems outside the realm of scheduling meetings for you via HouseWhisper. I'm best at helping you manage your schedule"
            }

        logger.info(f"Intents identified: {intents}")
        # Step 3: Prepare and run context chains
        chains_to_run = {}
        possible_intents = ['book', 'availability', 'heads down']
        if 'book' in intents:
            chains_to_run["book"] = booking_chain.ainvoke({"message": message})

        if 'availability' in intents:
            pass

        if 'heads down' in intents:
            pass

        context = {
            "availability_context": "",
            "heads_down_context": ""
        }
        if chains_to_run:
            chain_results = await asyncio.gather(*chains_to_run.values())
            context = dict(zip(chains_to_run.keys(), chain_results))

        # Step 4: Prepare final generation input
        response_input = {
            "chat_history": chat_history,
            "message": message,
            "summary": summary,
            "intents": intents,
            "booking_context": context['booking_context'],
            "availability_context": context['availability_context'],
            "heads_down_context": context['heads_down_context'],
        }

        response_result = await response_chain.ainvoke(response_input)

        return {
            "type": "assistant_response",
            "response": response_result["response"],
            "intents": intents,
            "chat_history": chat_history,
            "summary": summary.get('summary', ''),
        }

    return RunnableLambda(_run)


if __name__ == '__main__':
    chain = get_booking_agent_chain()
    payload = {"message": "Book me a time to show the Hindley property at 3:25pm tomorrow",
               "messages": []}
    resp = asyncio.run(chain.ainvoke(payload))
    print(resp['response'])