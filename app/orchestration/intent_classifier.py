
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_service import get_llm
from app.schemas.intent_schema import IntentClassification


# Get configured LLM
llm = get_llm()


# Convert LLM into a structured output model
structured_llm = llm.with_structured_output(
    IntentClassification
)


# Define classification instructions
prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are the Intent Classifier for
        Banarasi Bhaukal Travel Guru.

        Your responsibility is to understand the
        user's primary intention and classify it.

        Follow these routing rules:

        1. travel_information:
           General questions about destinations,
           history, culture, food, attractions,
           local transportation and travel guidance.
           Route to agent_a.

        2. trip_planning:
           Requests for personalized itineraries,
           trip schedules and travel plans.
           Route to agent_b.

        3. travel_search:
           Requests to search flights, hotels,
           trains, buses, activities or tickets.
           Route to agent_b.

        4. booking:
           Requests involving selecting or booking
           travel services.
           Route to agent_b.

        5. general:
           Greetings and queries unrelated to
           travel assistance.
           Route to general.

        Additional instructions:

        - Classify based on the actual meaning,
          not individual keywords.
        - Do not invent missing information.
        - Identify essential missing information
          when applicable.
        - If a query combines travel information
          with a request to create a personalized
          itinerary, prioritize trip_planning.
        - Do not claim that a booking has been made.
        - Return only the fields defined in
          the structured output schema.
        """
    ),

    (
        "human",
        "Classify this user query: {user_query}"
    )

])


# Create classifier chain
classifier_chain = prompt | structured_llm


def classify_intent(user_query: str):

    result = classifier_chain.invoke({
        "user_query": user_query
    })

    return result
