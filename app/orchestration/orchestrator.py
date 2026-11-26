
from app.orchestration.intent_classifier import classify_intent
from app.agents.booking_workflow import booking_states
from app.agents.agent_a import run_agent_a

from app.agents.agent_b import (
    run_agent_b,
    conversation_states
)

from app.agents.travel_search import travel_search_states


async def orchestrate(
    user_query: str,
    conversation_id: str = "default"
):

    print("\n========== ORCHESTRATOR ==========")

    # =====================================================
    # STEP 1: CHECK FOR AN EXISTING CONVERSATION
    # =====================================================
        # Continue an existing Booking conversation
    if conversation_id in booking_states:

        print("Continuing existing Booking conversation...")

        response = await run_agent_b(
            user_query=user_query,
            conversation_id=conversation_id
        )

        current_booking = booking_states.get(conversation_id)

        if current_booking is None:
            status = "completed"

        elif current_booking["booking_status"] == "ready_for_booking":
            status = "ready_for_booking"

        else:
            status = "awaiting_information"

        return {
            "status": status,
            "intent": "booking",
            "agent": "agent_b",
            "response": response
        }
    if conversation_id in conversation_states:

        print("Continuing existing Trip Planning conversation...")

        response = await run_agent_b(
            user_query=user_query,
            conversation_id=conversation_id
        )

        status = (
            "awaiting_information"
            if conversation_id in conversation_states
            else "completed"
        )

        return {
            "status": status,
            "intent": "trip_planning",
            "agent": "agent_b",
            "response": response
        }

    if conversation_id in travel_search_states:

        print("Continuing existing Travel Search conversation...")

        response = await run_agent_b(
            user_query=user_query,
            conversation_id=conversation_id
        )

        # Travel Search returns a dictionary
        if isinstance(response, dict):

            status = response.get(
                "status",
                "completed"
            )

        else:
            status = (
                "awaiting_information"
                if conversation_id in travel_search_states
                else "completed"
            )

        return {
            "status": status,
            "intent": "travel_search",
            "agent": "agent_b",
            "response": response
        }

    # =====================================================
    # STEP 2: CLASSIFY A NEW USER REQUEST
    # =====================================================

    classification = classify_intent(user_query)

    intent = classification.intent
    target_agent = classification.target_agent

    print("Detected Intent:", intent)
    print("Target Agent:", target_agent)

    # =====================================================
    # STEP 3: ROUTE TO AGENT B
    # =====================================================

    if target_agent == "agent_b":

        print("Forwarding request to Agent B...")

        response = await run_agent_b(
            user_query=user_query,
            conversation_id=conversation_id
        )

        # Get status from Travel Search response
        if isinstance(response, dict):

            status = response.get(
                "status",
                "completed"
            )

        # Trip Planning returns a string
        else:

            status = (
                "awaiting_information"
                if conversation_id in conversation_states
                else "completed"
            )

        return {
            "status": status,
            "intent": intent,
            "agent": "agent_b",
            "response": response
        }

    # =====================================================
    # STEP 4: HANDLE CLARIFICATION
    # =====================================================

    if classification.clarification_needed:

        return {
            "status": "clarification_required",
            "intent": intent,
            "agent": target_agent,
            "missing_information": classification.missing_information
        }

    # =====================================================
    # STEP 5: ROUTE TO AGENT A
    # =====================================================

    if target_agent == "agent_a":

        print("Forwarding request to Agent A...")

        response = await run_agent_a(user_query)

        return {
            "status": "completed",
            "intent": intent,
            "agent": "agent_a",
            "response": response
        }

    # =====================================================
    # STEP 6: HANDLE GENERAL CONVERSATION
    # =====================================================

    return {
        "status": "general",
        "intent": intent,
        "agent": "general",
        "message": "This is a general conversation."
    }
