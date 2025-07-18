import asyncio
from strands import Agent

from app.agents.config import bedrock_model
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    process_multilingual_order,
    order_recommendation_combo
)

MAIN_SYSTEM_PROMPT = """
You are an intelligent restaurant ordering assistant that helps customers place orders in any language.

Your primary capabilities:
1. Take and manage food orders
2. Provide menu recommendations
3. Handle orders in multiple languages (automatically detect and respond in the customer's language)
4. Answer questions about menu items, ingredients, and dietary restrictions

ROUTING LOGIC:
- For general ordering and English queries → Use the ordering_assistant_agent tool
- For non-English orders or when language translation is needed → Use the process_multilingual_order tool
- For combined recommendations with ordering → Use the order_recommendation_combo tool

Always be helpful, friendly, and respond in the customer's language when possible.
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[
        # Core ordering agents only
        ordering_assistant_agent,
        process_multilingual_order,
        order_recommendation_combo
    ],
    callback_handler=None
)

# Async function that iterates over streamed agent events
async def process_streaming_response():
    customer_query = "Hello, what is your special today? Can you recommend something vegetarian?"
    agent_stream = orchestrator.stream_async(customer_query)
    async for event in agent_stream:
        if "data" in event:
            print(event["data"], end="", flush=True)

if __name__ == "__main__":
    # Run the agent
    asyncio.run(process_streaming_response())
