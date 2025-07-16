from strands import Agent, tool
from strands_tools import retrieve, http_request

# Define specialized system prompts
RESEARCH_ASSISTANT_PROMPT = """
You are a specialized research assistant. Focus only on providing
factual, well-sourced information in response to research questions.
Always cite your sources when possible.
"""

PRODUCT_RECOMMENDATION_PROMPT = """
You are a specialized product recommendation assistant.
Provide personalized product suggestions based on user preferences.
Justify your recommendations clearly.
"""

TRAVEL_PLANNING_PROMPT = """
You are a specialized travel planning assistant.
Create detailed travel itineraries and recommendations based on user preferences.
Be specific and helpful.
"""

# === Research Assistant ===
@tool
def research_assistant(query: str) -> str:
    """
    Process and respond to research-related queries.
    """
    try:
        research_agent = Agent(
            system_prompt=RESEARCH_ASSISTANT_PROMPT,
            tools=[retrieve, http_request]
        )
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

# === Product Recommendation Assistant ===
@tool
def product_recommendation_assistant(query: str) -> str:
    """
    Handle product recommendation queries by suggesting appropriate products.
    """
    try:
        product_agent = Agent(
            system_prompt=PRODUCT_RECOMMENDATION_PROMPT,
            tools=[retrieve, http_request]
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

# === Trip Planning Assistant ===
@tool
def trip_planning_assistant(query: str) -> str:
    """
    Create travel itineraries and provide travel advice.
    """
    try:
        travel_agent = Agent(
            system_prompt=TRAVEL_PLANNING_PROMPT,
            tools=[retrieve, http_request]
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"
