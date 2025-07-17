import asyncio
from strands import Agent

from app.agents.config import bedrock_model
from app.agents.recommendation import (
    order_translation_agent,
    order_dietary_agent,
    order_recommendation_agent
)

MAIN_SYSTEM_PROMPT = """
You are an assistant that routes queries to specialized agents:
- For menu recommendations and food suggestions → Use the order_recommendation_agent tool
- For translating menu items and descriptions → Use the order_translation_agent tool
- For dietary restrictions and allergen information → Use the order_dietary_agent tool
- For simple questions not requiring specialized knowledge → Answer directly
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[
        order_recommendation_agent,
        order_translation_agent,
        order_dietary_agent
    ],
    callback_handler=None
)

# Async function that iterates over streamed agent events
async def process_streaming_response():
    customer_query = "Ano pwede kainin dito? May allergy ako sa mani at gatas."
    agent_stream = orchestrator.stream_async(customer_query)
    async for event in agent_stream:
        if "data" in event:
            print(event["data"], end="", flush=True)

if __name__ == "__main__":
    # Run the agent
    asyncio.run(process_streaming_response())
