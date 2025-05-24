from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from booking_agent.prompts import load_prompt
from booking_agent.llm.openai_llm import get_default_llm
from booking_agent.llm_tracing.tracer import LLMTracer


def get_response_chain():
    prompt = load_prompt("response")
    llm = get_default_llm(tags=["booking-response"], callbacks=[LLMTracer()])

    async def _response(inputs: dict) -> dict:
        prompt_text = prompt.format(
            chat_history=inputs.get("chat_history", ""),
            summary=inputs.get("summary", ""),
            message=inputs["message"],
            booking_context=inputs.get("booking_context", ""),
            availability_context=inputs.get("availability_context", ""),
            heads_down_context=inputs.get("heads_down_context", ""),
        )
        result = await llm.ainvoke(prompt_text)
        return {"response": result.content.strip()}

    return RunnableLambda(_response)


def get_streaming_response_chain():
    prompt = ChatPromptTemplate.from_template(load_prompt("qa_response"))
    llm = get_default_llm(tags=["booking-response"], callbacks=[LLMTracer()], streaming=True)

    # Define input mapping if your inputs aren't flat
    input_map = RunnableLambda(lambda inputs: {
        "chat_history": inputs.get("chat_history", ""),
        "summary": inputs.get("summary", ""),
        "message": inputs["message"],
    })

    return input_map | prompt | llm | StrOutputParser()


