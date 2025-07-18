import asyncio
from strands import Agent

from app.agents.config import bedrock_model
from app.agents.recommendation import (
    order_translation_agent,
    order_dietary_agent,
    order_recommendation_agent
)
from app.agents.menu_agent import (
    get_menu_recommendations,
    get_allergen_information
)
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    recommendation_agent,
    translation_agent,
    process_multilingual_order,
    order_recommendation_combo
)

MAIN_SYSTEM_PROMPT = """
You are an intelligent restaurant assistant that routes customer queries to specialized agents:

ORDER MANAGEMENT:
- For taking orders, order assistance, and order modifications → Use the ordering_assistant_agent tool
- For multilingual order processing (non-English orders) → Use the process_multilingual_order tool
- For combined recommendations and ordering → Use the order_recommendation_combo tool

RECOMMENDATIONS:
- For personalized menu recommendations → Use the recommendation_agent tool
- For general menu recommendations and food suggestions → Use the order_recommendation_agent tool
- For specific menu recommendations based on dietary preferences → Use the get_menu_recommendations tool

TRANSLATION:
- For translating customer messages and orders → Use the translation_agent tool
- For translating menu items and descriptions → Use the order_translation_agent tool

DIETARY & ALLERGEN INFO:
- For general dietary restrictions and allergen information → Use the order_dietary_agent tool
- For detailed allergen information and analysis → Use the get_allergen_information tool

ROUTING LOGIC:
1. If customer is placing an order or asking about ordering → Use ordering agents
2. If customer needs recommendations → Use recommendation agents
3. If customer is speaking in a non-English language → Use translation agents
4. If customer has dietary concerns → Use dietary/allergen agents
5. For simple questions not requiring specialized knowledge → Answer directly

Always be helpful, friendly, and ensure accurate routing to provide the best customer experience.
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[
        # Ordering agents
        ordering_assistant_agent,
        process_multilingual_order,
        order_recommendation_combo,
        
        # Recommendation agents
        recommendation_agent,
        order_recommendation_agent,
        get_menu_recommendations,
        
        # Translation agents
        translation_agent,
        order_translation_agent,
        
        # Dietary and allergen agents
        order_dietary_agent,
        get_allergen_information
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
