from strands import Agent, tool
from strands_tools import retrieve, http_request
from app.agents.config import bedrock_model

# Define specialized system prompts
ORDER_RECOMMENDATION_PROMPT = """
You are a specialized product recommendation assistant.
Provide personalized product suggestions based on user preferences.
Justify your recommendations clearly.
"""

ORDER_TRANSLATION_PROMPT = """
You are a specialized order translation assistant.
When a user asks in a language other than English, translate their request into English.
Respond on the same language as the user as well as the english translation.
Always ensure the translation is accurate and contextually appropriate.
If the user asks for a translation, provide it in the same language as the original request.
"""

ORDER_DIETARY_PROMPT = """
You are a specialized dietary assistant.
When a user asks about dietary preferences or restrictions, provide tailored advice.
Consider common dietary needs such as vegetarian, vegan, gluten-free, etc.
Also consider cultural dietary practices and allergies.
Always ensure the advice is practical and easy to follow.
"""

@tool
def order_translation_agent(query: str) -> str:
    """
    Process and respond to research-related queries.
    """
    try:
        research_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDER_TRANSLATION_PROMPT,
            tools=[retrieve, http_request]
        )
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def order_recommendation_agent(query: str) -> str:
    """
    Handle product recommendation queries by suggesting appropriate products.
    """
    try:
        product_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDER_RECOMMENDATION_PROMPT,
            tools=[retrieve, http_request]
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

@tool
def order_dietary_agent(query: str) -> str:
    """
    Create travel itineraries and provide travel advice.
    """
    try:
        travel_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDER_DIETARY_PROMPT,
            tools=[retrieve, http_request]
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"