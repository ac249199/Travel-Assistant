
import asyncio

from app.orchestration.orchestrator import orchestrate
from app.agents.booking_workflow import (
    initialize_booking,
    booking_states
)


async def main():

    conversation_id = "booking_orchestrator_test_1"

    # Clear any previous test state
    booking_states.pop(conversation_id, None)

    # Initialize a selected hotel booking
    print("\n========== INITIALIZE BOOKING ==========")

    response = initialize_booking(
        conversation_id,
        "hotel",
        "Shree Shyam Palace"
    )

    print(response)

    # Turn 1: Customer name
    print("\n========== TURN 1: CUSTOMER NAME ==========")

    response = await orchestrate(
        "Rahul Sharma",
        conversation_id
    )

    print(response)

    # Turn 2: Customer email
    print("\n========== TURN 2: CUSTOMER EMAIL ==========")

    response = await orchestrate(
        "rahul@example.com",
        conversation_id
    )

    print(response)

    # Turn 3: Confirm booking request
    print("\n========== TURN 3: CONFIRM BOOKING ==========")

    response = await orchestrate(
        "Yes, confirm",
        conversation_id
    )

    print(response)

    # Verify final state
    print("\n========== FINAL VERIFICATION ==========")

    final_state = booking_states.get(conversation_id)

    if final_state:
        print("Final booking status:", final_state["booking_status"])
        assert final_state["booking_status"] == "ready_for_booking"
        print("\nORCHESTRATOR BOOKING TEST PASSED!")
    else:
        raise AssertionError("Booking state unexpectedly disappeared.")


if __name__ == "__main__":
    asyncio.run(main())
