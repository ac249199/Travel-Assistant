from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_service import get_llm
from app.schemas.agent_b_schema import AgentBWorkflow


llm = get_llm()

structured_llm = llm.with_structured_output(
    AgentBWorkflow
)



prompt = ChatPromptTemplate.from_messages([

    ("system", """
    You are the Workflow Router for Agent B
    of Banarasi Bhaukal Travel Guru.

    Your job is to identify which workflow
    should handle the user's request.

    Available workflows:

    1. trip_planning:
       Select when the user wants a complete
       travel itinerary or day-wise trip plan.

    2. travel_search:
       Select when the user wants to search for:
       - Hotels
       - Flights
       - Trains

    3. booking:
       Select when the user wants to book,
       reserve, or proceed with a selected
       travel service.

    Important rules:

    - Select only one workflow.
    - Do not execute the workflow.
    - Do not answer the user's travel query.
    - Only classify the request.
    - Hotel, flight and train searches must
      always be classified as travel_search.
    - Do not classify restaurant, sightseeing,
      or local transport searches as travel_search.
    """),

    ("human", "User Query: {user_query}")

])


workflow_router = prompt | structured_llm


def route_agent_b(user_query: str):

    result = workflow_router.invoke({
        "user_query": user_query
    })

    return result