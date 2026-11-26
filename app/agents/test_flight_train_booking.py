
import asyncio

from app.agents.agent_b import run_agent_b
from app.agents.travel_search import travel_search_results
from app.agents.booking_workflow import booking_states


async def test_flight_booking():

    conversation_id = "flight_booking_test"

    # Mock flight search results
    travel_search_results[conversation_id] = {
        "status": "completed",
        "search_category": "flight",
        "flights": [
            {
                "flights": [
                    {
                        "airline": "IndiGo",
                        "flight_number": "6E 201",
                        "departure_airport": {
                            "name": "Varanasi Airport",
                            "id": "VNS"
                        },
                        "arrival_airport": {
                            "name": "Delhi Airport",
                            "id": "DEL"
                        }
                    }
                ],
                "price": 4500,
                "total_duration": 95
            }
        ]
    }

    print("\n========== FLIGHT BOOKING TEST ==========")

    response = await run_agent_b(
        "Book option 1",
        conversation_id
    )
    print(response)

    response = await run_agent_b(
        "Rahul Sharma",
        conversation_id
    )
    print(response)

    response = await run_agent_b(
        "rahul@example.com",
        conversation_id
    )
    print(response)

    response = await run_agent_b(
        "Yes",
        conversation_id
    )
    print(response)

    state = booking_states[conversation_id]

    print("\nFlight final status:", state["booking_status"])
    print("Selected flight:", state["selected_option"]["flights"][0]["airline"])


async def test_train_booking():

    conversation_id = "train_booking_test"

    # Mock train search results
    travel_search_results[conversation_id] = {
        "status": "completed",
        "search_category": "train",
        "trains": [
            {
                "train_number": "12560",
                "extended_train_name": "Shiv Ganga Express",
                "from_station_name": "Varanasi Junction",
                "from_station_code": "BSB",
                "to_station_name": "New Delhi",
                "to_station_code": "NDLS",
                "departure_time": "19:30",
                "arrival_time": "07:00",
                "duration_minutes": 690,
                "classes": ["SL", "3A", "2A"]
            }
        ]
    }

    print("\n========== TRAIN BOOKING TEST ==========")

    response = await run_agent_b(
        "Book option 1",
        conversation_id
    )
    print(response)

    response = await run_agent_b(
        "Rahul Sharma",
        conversation_id
    )
    print(response)

    response = await run_agent_b(
        "rahul@example.com",
        conversation_id
    )
    print(response)

    response = await run_agent_b(
        "Yes",
        conversation_id
    )
    print(response)

    state = booking_states[conversation_id]

    print("\nTrain final status:", state["booking_status"])
    print("Selected train:", state["selected_option"]["extended_train_name"])


async def main():

    await test_flight_booking()
    await test_train_booking()


if __name__ == "__main__":
    asyncio.run(main())
