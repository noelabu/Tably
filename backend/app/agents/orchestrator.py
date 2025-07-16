from strands import Agent

from app.agents.config import bedrock_model
from app.agents.recommendation import (
    product_recommendation_assistant,
    research_assistant,
    trip_planning_assistant
)

MAIN_SYSTEM_PROMPT = """
You are an assistant that routes queries to specialized agents:
- For research questions and factual information → Use the research_assistant tool
- For product recommendations and shopping advice → Use the product_recommendation_assistant tool
- For travel planning and itineraries → Use the trip_planning_assistant tool
- For simple questions not requiring specialized knowledge → Answer directly
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    model=bedrock_model,
    tools=[
        research_assistant,
        product_recommendation_assistant,
        trip_planning_assistant
    ]
)

if __name__ == "__main__":
    customer_query = "I'm looking for hiking boots for a trip to Patagonia next month"
    response = orchestrator(customer_query)
    print(response)
