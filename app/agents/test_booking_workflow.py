
import asyncio

from app.agents.agent_b import run_agent_b
from app.agents.travel_search import travel_search_results
from app.agents.booking_workflow import booking_states


async def main():

    conversation_id = "booking_test_001"

    # 1. Insert mock hotel search results
    travel_search_results[conversation_id] = {
        "status": "completed",
        "search_category": "hotel",
        "hotels": [
            {
                "name": "Hotel Amrit Heritage",
                "hotel_id": "HOTEL001",
                "price": 6748
            },
            {
                "name": "Shree Shyam Palace",
                "hotel_id": "HOTEL002",
                "price": 4227
            },
            {
                "name": "Madpackers Varanasi",
                "hotel_id": "HOTEL003",
                "price": 19090
            }
        ]
    }

    # 2. Select hotel
    print("\n--- SELECT HOTEL ---")

    response = await run_agent_b(
        "Book option 2",
        conversation_id
    )

    print(response)

    # 3. Provide customer name
    print("\n--- CUSTOMER NAME ---")

    response = await run_agent_b(
        "Rahul Sharma",
        conversation_id
    )

    print(response)

    # 4. Provide email
    print("\n--- CUSTOMER EMAIL ---")

    response = await run_agent_b(
        "rahul@example.com",
        conversation_id
    )

    print(response)

    # 5. Confirm booking request
    print("\n--- CONFIRM BOOKING ---")

    response = await run_agent_b(
        "Yes",
        conversation_id
    )

    print(response)

    # 6. Verify final state
    print("\n--- FINAL BOOKING STATE ---")

    print(
        booking_states[conversation_id]["booking_status"]
    )

    print(
        "Selected hotel:",
        booking_states[conversation_id]["selected_option"]["name"]
    )


if __name__ == "__main__":
    asyncio.run(main())
