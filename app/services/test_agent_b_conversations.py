
import asyncio
from datetime import date
from types import SimpleNamespace

from app.orchestration import orchestrator
from app.agents import agent_b
from app.agents import travel_search


# =====================================================
# 1. MOCK INTENT CLASSIFIER AND WORKFLOW ROUTER
# =====================================================

def mock_classify_intent(user_query):
    return SimpleNamespace(
        intent="travel_search",
        target_agent="agent_b",
        clarification_needed=False,
        missing_information=[]
    )


def mock_route_agent_b(user_query):
    return SimpleNamespace(workflow="travel_search")


# =====================================================
# 2. MOCK HOTEL API
# =====================================================

def mock_get_stayapi_destination(destination):
    print("\nMOCK: StayAPI destination lookup")

    return {
        "success": True,
        "dest_id": "-2114217",
        "dest_type": "CITY"
    }


def mock_search_hotels(
    dest_id,
    dest_type,
    checkin,
    checkout,
    adults,
    rooms
):
    print("\nMOCK: StayAPI hotel search")
    print("Check-in:", checkin)
    print("Check-out:", checkout)
    print("Guests:", adults)

    return {
        "success": True,
        "hotels": []
    }


def mock_format_stayapi_hotels(results):
    return [
        {
            "name": "Hotel Amrit Heritage Guest House",
            "address": "Varanasi, Uttar Pradesh",
            "display_price": "₹6,748",
            "guest_rating": 8.5,
            "review_count": 120
        },
        {
            "name": "Hotel Taposthali",
            "address": "Varanasi, Uttar Pradesh",
            "display_price": "₹5,400",
            "guest_rating": 8.2,
            "review_count": 95
        }
    ]


# =====================================================
# 3. MOCK FLIGHT API
# =====================================================

def mock_resolve_airport(city):
    airports = {
        "varanasi": {
            "success": True,
            "airport_code": "VNS",
            "airport_name": "Varanasi Airport"
        },
        "delhi": {
            "success": True,
            "airport_code": "DEL",
            "airport_name": "Delhi Airport"
        }
    }

    return airports.get(
        city.lower(),
        {
            "success": False,
            "message": "Airport not found."
        }
    )



def mock_search_flights(
    departure_id,
    arrival_id,
    outbound_date,
    return_date=None,
    adults=1,
    travel_class=1
):
    print("\nMOCK: SerpApi flight search")
    print("From:", departure_id)
    print("To:", arrival_id)
    print("Date:", outbound_date)
    print("Adults:", adults)

    return {
        "best_flights": [
            {
                "flights": [
                    {
                        "airline": "IndiGo",
                        "flight_number": "6E 201",
                        "departure_airport": {
                            "name": "Varanasi Airport",
                            "id": departure_id,
                            "time": f"{outbound_date} 08:00"
                        },
                        "arrival_airport": {
                            "name": "Delhi Airport",
                            "id": arrival_id,
                            "time": f"{outbound_date} 09:35"
                        },
                        "duration": 95,
                        "travel_class": "Economy"
                    }
                ],
                "price": 4500
            }
        ],
        "other_flights": []
    }

def mock_format_flight_results(results):
    return (
        "1. IndiGo 6E 201\n"
        "From: Varanasi Airport (VNS)\n"
        "Departure: 08:00\n"
        "To: Delhi Airport (DEL)\n"
        "Arrival: 09:35\n"
        "Duration: 95 minutes\n"
        "Price: 4500 INR"
    )


# =====================================================
# 4. MOCK TRAIN API
# =====================================================

def mock_resolve_train_station(location):
    print("\nMOCK: RailCore station resolution:", location)

    stations = {
        "varanasi": [
            {
                "station_code": "BSB",
                "station_name": "Varanasi Junction",
                "display_name": "Varanasi Junction (BSB)"
            }
        ],
        "delhi": [
            {
                "station_code": "NDLS",
                "station_name": "New Delhi",
                "display_name": "New Delhi (NDLS)"
            }
        ]
    }

    return {
        "stations": stations.get(location.lower(), [])
    }



def mock_search_trains(
    from_station,
    to_station,
    journey_date,
    match="station"
):
    print("\nMOCK: RailCore train search")
    print("From:", from_station)
    print("To:", to_station)
    print("Date:", journey_date)

    return {
        "success": True,
        "data": {
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
    }

# =====================================================
# 5. APPLY MOCKS
# =====================================================

orchestrator.classify_intent = mock_classify_intent
agent_b.route_agent_b = mock_route_agent_b

# IMPORTANT:
# We are NOT mocking collect_travel_search_details.
# The actual LLM extraction will run.

# Hotel mocks
travel_search.get_stayapi_destination = mock_get_stayapi_destination
travel_search.search_hotels = mock_search_hotels
travel_search.format_stayapi_hotels = mock_format_stayapi_hotels

# Flight mocks
travel_search.resolve_airport = mock_resolve_airport
travel_search.search_flights = mock_search_flights
travel_search.format_flight_results = mock_format_flight_results

# Train mocks
travel_search.resolve_train_station = mock_resolve_train_station
travel_search.search_trains = mock_search_trains


# =====================================================
# 6. HELPER TO SEND A CONVERSATION TURN
# =====================================================

async def send_turn(query, conversation_id):

    print("\nUSER:", query)

    result = await orchestrator.orchestrate(
        user_query=query,
        conversation_id=conversation_id
    )

    print("STATUS:", result.get("status"))
    print("RESPONSE:", result.get("response"))

    return result


# =====================================================
# 7. HOTEL MULTI-TURN TEST
# =====================================================

async def test_hotel_conversation():

    conversation_id = "hotel_conversation_test"

    print("\n========================================")
    print("HOTEL MULTI-TURN CONVERSATION")
    print("========================================")

    # Turn 1: Destination
    result = await send_turn(
        "Find a hotel in Varanasi",
        conversation_id
    )

    assert result["status"] == "awaiting_information"

    # Turn 2: Dates
    result = await send_turn(
        "Check-in 10 December 2026 and check-out 12 December 2026",
        conversation_id
    )

    assert result["status"] == "awaiting_information"

    # Turn 3: Guests
    result = await send_turn(
        "2 adults",
        conversation_id
    )

    assert result["status"] == "completed"

    assert (
        "Hotel Amrit Heritage Guest House"
        in result["response"]["formatted_message"]
    )

    assert conversation_id not in travel_search.travel_search_states

    print("\nHOTEL MULTI-TURN TEST PASSED!")


# =====================================================
# 8. FLIGHT MULTI-TURN TEST
# =====================================================

async def test_flight_conversation():

    conversation_id = "flight_conversation_test"

    print("\n========================================")
    print("FLIGHT MULTI-TURN CONVERSATION")
    print("========================================")

    # Turn 1: Origin and destination
    result = await send_turn(
        "Find a one-way flight from Varanasi to Delhi",
        conversation_id
    )

    assert result["status"] == "awaiting_information"

    # Turn 2: Date and passenger details
    result = await send_turn(
        "15 December 2026 for 1 adult in economy",
        conversation_id
    )

    assert result["status"] == "completed"

    assert result["response"]["search_category"] == "flight"

    assert "IndiGo 6E 201" in (
        result["response"]["formatted_message"]
    )

    assert conversation_id not in travel_search.travel_search_states

    print("\nFLIGHT MULTI-TURN TEST PASSED!")


# =====================================================
# 9. TRAIN MULTI-TURN TEST
# =====================================================

async def test_train_conversation():

    conversation_id = "train_conversation_test"

    print("\n========================================")
    print("TRAIN MULTI-TURN CONVERSATION")
    print("========================================")

    # Turn 1: Origin and destination
    result = await send_turn(
        "Find a train from Varanasi to Delhi",
        conversation_id
    )

    assert result["status"] == "awaiting_information"

    # Turn 2: Journey date
    result = await send_turn(
        "16 December 2026",
        conversation_id
    )

    assert result["status"] == "completed"

    assert result["response"]["search_category"] == "train"

    assert "Shiv Ganga Express" in (
        result["response"]["formatted_message"]
    )

    assert conversation_id not in travel_search.travel_search_states

    print("\nTRAIN MULTI-TURN TEST PASSED!")


# =====================================================
# 10. RUN ALL TESTS
# =====================================================

async def main():

    conversation_ids = [
        "hotel_conversation_test",
        "flight_conversation_test",
        "train_conversation_test"
    ]

    try:
        await test_hotel_conversation()
        await test_flight_conversation()
        await test_train_conversation()

        print("\n========================================")
        print("ALL MULTI-TURN CONVERSATION TESTS PASSED!")
        print("========================================")

    finally:
        for conversation_id in conversation_ids:
            travel_search.travel_search_states.pop(
                conversation_id, None
            )


if __name__ == "__main__":
    asyncio.run(main())
