import asyncio
from strands import Agent

from app.agents.config import bedrock_model
from app.agents.recommendation import (
    order_translation_agent,
    order_dietary_agent,
    order_recommendation_agent
)
from app.agents.menu_agent import (
    menu_intelligent_agent,
    analyze_menu_image,
    get_menu_recommendations,
    search_menu_items,
    get_allergen_information
)

MAIN_SYSTEM_PROMPT = """
You are an assistant that routes queries to specialized agents:
- For general menu recommendations and food suggestions → Use the order_recommendation_agent tool
- For translating menu items and descriptions → Use the order_translation_agent tool
- For general dietary restrictions and allergen information → Use the order_dietary_agent tool
- For comprehensive menu analysis and intelligence → Use the menu_intelligent_agent tool
- For analyzing menu images and extracting structured data → Use the analyze_menu_image tool
- For specific menu recommendations based on dietary preferences → Use the get_menu_recommendations tool
- For searching specific menu items or ingredients → Use the search_menu_items tool
- For detailed allergen information and analysis → Use the get_allergen_information tool
- For simple questions not requiring specialized knowledge → Answer directly
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[
        order_recommendation_agent,
        order_translation_agent,
        order_dietary_agent,
        menu_intelligent_agent,
        analyze_menu_image,
        get_menu_recommendations,
        search_menu_items,
        get_allergen_information
    ],
    callback_handler=None
)

# Async function that iterates over streamed agent events
async def process_streaming_response():
    customer_query = "Can you analyze this menu and recommend dishes that are safe for someone with nut and dairy allergies?"
    agent_stream = orchestrator.stream_async(customer_query)
    async for event in agent_stream:
        if "data" in event:
            print(event["data"], end="", flush=True)

if __name__ == "__main__":
    # Run the agent
    asyncio.run(process_streaming_response())
