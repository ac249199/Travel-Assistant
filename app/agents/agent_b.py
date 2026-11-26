
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_service import get_llm

from app.schemas.trip_schema import TripPlanningRequest
from app.schemas.trip_extraction_schema import TripDetailsExtraction

from app.agents.agent_b_router import route_agent_b
from app.agents.trip_planner import generate_trip_plan

from app.agents.travel_search import (
    run_travel_search,
    travel_search_states,
    travel_search_results,
    select_travel_option
)

from app.agents.booking_workflow import (
    booking_states,
    collect_booking_details,
    confirm_booking,
    initialize_booking_from_search
)


llm = get_llm()


# =========================================================
# 1. TRIP PLANNING CONVERSATION STATE
# =========================================================

conversation_states = {}


# =========================================================
# 2. STRUCTURED OUTPUT FOR TRIP DETAILS
# =========================================================

trip_request_llm = llm.with_structured_output(
    TripDetailsExtraction
)


# =========================================================
# 3. TRIP DETAILS EXTRACTION PROMPT
# =========================================================

trip_extraction_prompt = ChatPromptTemplate.from_messages([

    ("system", """
    You are a Trip Details Extractor for
    Banarasi Bhaukal Travel Guru.

    Extract the following information from the
    latest user message:

    1. destination
    2. duration_days
    3. travellers

    Rules:
    - Extract only information explicitly provided
      in the latest user message.
    - Do not invent missing details.
    - If a detail is not mentioned, return None.
    - Do not infer values from previous messages.
    """),

    ("human", "{user_query}")

])


trip_request_chain = trip_extraction_prompt | trip_request_llm


# =========================================================
# 4. TRIP PLANNING WORKFLOW
# =========================================================

def run_trip_planning(
    user_query: str,
    conversation_id: str
):

    # Step 1: Get existing trip state
    trip_state = conversation_states.get(conversation_id)

    # Step 2: Initialize state if this is a new request
    if trip_state is None:

        trip_state = {
            "destination": None,
            "duration_days": None,
            "travellers": None
        }

        conversation_states[conversation_id] = trip_state

    # Step 3: Extract details from latest message
    extracted_details = trip_request_chain.invoke({
        "user_query": user_query
    })

    print("\nExtracted Trip Details:", extracted_details)

    # Step 4: Update existing state
    if extracted_details.destination is not None:
        trip_state["destination"] = extracted_details.destination

    if extracted_details.duration_days is not None:
        trip_state["duration_days"] = extracted_details.duration_days

    if extracted_details.travellers is not None:
        trip_state["travellers"] = extracted_details.travellers

    print("\nUpdated Trip State:", trip_state)

    # Step 5: Identify missing information
    missing_information = []

    if not trip_state["destination"]:
        missing_information.append("destination")

    if trip_state["duration_days"] is None:
        missing_information.append("trip duration")

    if trip_state["travellers"] is None:
        missing_information.append("number of travellers")

    # Step 6: Ask follow-up questions
    if missing_information:

        return (
            "I need a little more information to plan your trip. "
            "Please provide: "
            + ", ".join(missing_information)
            + "."
        )

    # Step 7: Create validated trip request
    trip_request = TripPlanningRequest(
        destination=trip_state["destination"],
        duration_days=trip_state["duration_days"],
        travellers=trip_state["travellers"]
    )

    # Step 8: Generate itinerary
    result = generate_trip_plan(trip_request)

    # Step 9: Clear state after successful completion
    conversation_states.pop(conversation_id, None)

    return result


# =========================================================
# 5. MAIN AGENT B
# =========================================================

async def run_agent_b(
    user_query: str,
    conversation_id: str = "default"
):

    print("\n========== AGENT B ==========")

        # Step 0: Continue an existing Booking workflow
    if conversation_id in booking_states:

        print("Continuing existing Booking workflow...")

        booking_state = booking_states[conversation_id]

        booking_status = booking_state["booking_status"]

        if booking_status == "collecting_details":

            return collect_booking_details(
                conversation_id=conversation_id,
                user_query=user_query
            )

        elif booking_status == "awaiting_confirmation":

            return confirm_booking(
                conversation_id=conversation_id,
                user_query=user_query
            )

        elif booking_status == "ready_for_booking":

            return (
                "Your booking request is already confirmed "
                "and is awaiting booking submission. "
                "No reservation or payment has been made."
            )

    # Step 1: Continue an existing Travel Search
    if conversation_id in travel_search_states:

        print("Continuing existing Travel Search...")

        return await run_travel_search(
            user_query=user_query,
            conversation_id=conversation_id
        )

    # Step 2: Continue an existing Trip Planning request
    if conversation_id in conversation_states:

        print("Continuing existing Trip Planning...")

        return run_trip_planning(
            user_query=user_query,
            conversation_id=conversation_id
        )

    # Step 3: Identify the requested workflow
    workflow_result = route_agent_b(user_query)

    workflow = workflow_result.workflow

    print("Agent B selected workflow:", workflow)

    # Step 4: Route to Travel Search
    if workflow == "travel_search":

        print("Forwarding request to Travel Search...")

        return await run_travel_search(
            user_query=user_query,
            conversation_id=conversation_id
        )

    # Step 5: Route to Trip Planning
    elif workflow == "trip_planning":

        print("Forwarding request to Trip Planning...")

        return run_trip_planning(
            user_query=user_query,
            conversation_id=conversation_id
        )

    
    # Step 6: Booking workflow
    elif workflow == "booking":

        print("Starting Booking workflow...")

        # Check whether completed search results exist
        if conversation_id not in travel_search_results:

            return (
                "I couldn't find any recent travel search results. "
                "Please search for a hotel, flight or train first."
            )

        # Identify the selected option
        selection_result = select_travel_option(
            conversation_id=conversation_id,
            user_query=user_query
        )

        if selection_result["status"] != "selected":
            return selection_result["message"]

        # Initialize booking using the selected result
        return initialize_booking_from_search(
            conversation_id=conversation_id,
            selection_result=selection_result
        )

    # Step 7: Unknown workflow
    return "Unable to identify the requested workflow."