
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_service import get_llm
from app.rag.itinerary_retriever import retrieve_itinerary
from app.schemas.trip_schema import TripPlanningRequest


# Initialize LLM
llm = get_llm()


# Trip Planner Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an intelligent travel planner for
    Banarasi Bhaukal Travel Guru.

    Your job is to create customized travel itineraries
    based on the user's requirements.

    The retrieved itinerary context is a knowledge source,
    not a fixed itinerary that must be copied.

    Follow these rules:

    1. Understand the user's requested destination
       and trip duration.

    2. Generate exactly the requested number of days.

    3. You are free to reorganize, combine, distribute
       and prioritize activities across different days.

    4. Do not blindly copy the original PDF itinerary.

    5. Adapt the itinerary according to the user's
       interests and preferences when provided.

    6. Avoid repeating the same activities unnecessarily.

    7. Make the itinerary practical and well organized.

    8. Use retrieved information as the primary source
       for places, restaurants and activities.

    9. Do not invent factual information such as
       opening hours, prices or travel times.

    10. If information is insufficient, clearly
        communicate the limitation.

    11. The final itinerary must match the user's
        requested duration exactly.

    12. If the retrieved context does not contain
        sufficient information about the requested
        destination, do not fabricate an itinerary.
        Explain that the available travel knowledge
        does not sufficiently cover that destination.
    13. Never introduce new place names, attractions,
        restaurants or activities that are not supported
        by the retrieved context.

        If a suggested activity is not supported by
        the context, omit it instead of guessing.    
    """),

    ("human", """
    Trip Details:

    Destination: {destination}
    Duration: {duration_days} days
    Travellers: {travellers}

    Retrieved Itinerary Context:

    {context}

    Generate the customized travel itinerary.
    """)
])


def generate_trip_plan(request: TripPlanningRequest):

    # Step 1: Retrieve relevant itinerary chunks
    query = (
        f"Create a {request.duration_days}-day itinerary "
        f"for {request.destination}"
    )

    retrieved_chunks = retrieve_itinerary(
        query,
        top_k=5,
        duration_days=request.duration_days
    )

    # Step 2: Combine retrieved chunks into context
    context = "\n\n".join(retrieved_chunks)

    # Step 3: Prepare the LLM chain
    chain = prompt | llm

    # Step 4: Generate itinerary
    response = chain.invoke({
        "destination": request.destination,
        "duration_days": request.duration_days,
        "travellers": request.travellers,
        "context": context
    })

    # Step 5: Return generated itinerary
    return response.content
