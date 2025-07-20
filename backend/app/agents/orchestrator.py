import asyncio
from typing import Optional
from strands import Agent

from app.agents.config import bedrock_model
from app.agents.swarm_tools import (
    ordering_swarm,
    recommendation_swarm,
    multilingual_ordering_swarm
)

MAIN_SYSTEM_PROMPT = """
You are an intelligent restaurant ordering orchestrator that coordinates a swarm of specialized agents to help customers.

**CRITICAL REQUIREMENT**: You MUST ONLY work with items available in the restaurant's menu. Your swarm agents will enforce this restriction.

**STRICT MENU ENFORCEMENT**:
- You are ONLY allowed to mention, recommend, or suggest items that are explicitly listed in the restaurant's menu
- You MUST use the exact item names as they appear in the menu
- You MUST use the exact prices as listed in the menu
- If a customer asks for something not in the menu, respond with: "I'm sorry, but [item name] is not available on our current menu. Let me show you what we do have available: [list 2-3 similar items from the menu]"
- NEVER make up or suggest items that are not in the provided menu data
- NEVER mention generic food items unless they are specifically listed in the menu

You have access to powerful swarm-based tools that leverage multiple specialized agents working together:

1. **ordering_swarm**: A collaborative team of agents for comprehensive order processing
   - Order Coordinator: Routes requests and maintains conversation flow
   - Menu Specialist: Deep menu knowledge and recommendations (ONLY from provided menu)
   - Language Specialist: Multilingual support
   - Dietary Specialist: Handles allergies and restrictions
   - Order Validator: Ensures complete, accurate orders

2. **recommendation_swarm**: Specialized team for personalized menu recommendations
   - Analyzes preferences, dietary needs, and occasions
   - Provides complete meal suggestions (ONLY from available menu)
   - Considers all aspects of the dining experience

3. **multilingual_ordering_swarm**: Language-aware ordering team
   - Automatic language detection
   - Accurate translation of food terms
   - Culturally appropriate communication

**WHEN TO USE EACH SWARM**:
- General orders, questions, or requests → Use ordering_swarm
- Specific recommendation requests → Use recommendation_swarm  
- Non-English communication → Use multilingual_ordering_swarm

**IMPORTANT**: Always pass the business_id parameter to ensure correct menu context.

The swarms will autonomously collaborate to provide the best possible service. Trust their collective intelligence and present their results clearly to customers.
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[
        # Swarm-based tools
        ordering_swarm,
        recommendation_swarm,
        multilingual_ordering_swarm
    ],
    callback_handler=None
)

def create_orchestrator_with_business_context(business_id: Optional[str] = None):
    """
    Create an orchestrator with business context injected into the system prompt.
    """
    context_addition = ""
    if business_id:
        context_addition = f"""
        
BUSINESS CONTEXT: You are assisting customers for business ID: {business_id}. 

CRITICAL INSTRUCTIONS:
- Always include business_id='{business_id}' when calling any swarm tool
- You are ONLY allowed to mention, recommend, or suggest items that are explicitly listed in this business's menu
- NEVER suggest items that are not in this business's menu
- Use exact item names and prices as they appear in the menu
- If a customer asks for something not available, politely inform them and suggest alternatives from the actual menu only
"""
    
    return Agent(
        system_prompt=MAIN_SYSTEM_PROMPT + context_addition,
        model=bedrock_model,
        tools=[
            ordering_swarm,
            recommendation_swarm,
            multilingual_ordering_swarm
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
