
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
# 2. MOCK EXTRACTION
# =====================================================

def mock_collect_travel_search_details(user_query, conversation_id):

    query = user_query.lower()

    if "hotel" in query:
        state = {
            "search_category": "hotel",
            "destination": "Varanasi",
            "check_in_date": date(2026, 11, 25),
            "check_out_date": date(2026, 11, 27),
            "guests": 2,
            "budget_per_night": None,
            "preferences": []
        }

    elif "flight" in query:
        state = {
            "search_category": "flight",
            "origin": "Varanasi",
            "destination": "Delhi",
            "departure_date": date(2026, 12, 10),
            "return_date": None,
            "trip_type": "one_way",
            "adults": 1,
            "children": 0,
            "infants": 0,
            "travel_class": 1,
            "preferences": []
        }

    elif "train" in query:
        state = {
            "search_category": "train",
            "origin": "Varanasi",
            "destination": "Delhi",
            "journey_date": date(2026, 12, 10),
            "train_class": None,
            "quota": None,
            "origin_station_code": None,
            "origin_station_name": None,
            "destination_station_code": None,
            "destination_station_name": None,
            "_pending_station_field": None,
            "_pending_station_candidates": [],
            "preferences": []
        }

    else:
        return {
            "status": "error",
            "message": "Unsupported test request."
        }

    travel_search.travel_search_states[conversation_id] = state

    return {
        "status": "ready_to_search",
        "search_request": state
    }


# =====================================================
# 3. MOCK HOTEL SERVICES
# =====================================================

def mock_get_stayapi_destination(destination):
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
            "review_count": 120,
            "room_name": "Deluxe Room"
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
# 4. MOCK FLIGHT SERVICES
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
    return {
        "best_flights": [],
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
# 5. MOCK TRAIN SERVICES
# =====================================================

def mock_resolve_train_station(location):

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
    return {
        "success": True,
        "data": {
            "trains": [
                {
                    "train_number": "12560",
                    "extended_train_name": "Shiv Ganga Express",
                    "from_station_name": "Varanasi Junction",
                    "to_station_name": "New Delhi",
                    "departure_time": "19:30",
                    "arrival_time": "07:00",
                    "duration_minutes": 690,
                    "classes": ["SL", "3A", "2A"]
                }
            ]
        }
    }


# =====================================================
# 6. APPLY MOCKS
# =====================================================

orchestrator.classify_intent = mock_classify_intent
agent_b.route_agent_b = mock_route_agent_b

travel_search.collect_travel_search_details = (
    mock_collect_travel_search_details
)

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
# 7. HOTEL SEARCH TEST
# =====================================================

async def test_hotel_search(conversation_id):

    result = await orchestrator.orchestrate(
        user_query="Find hotels in Varanasi",
        conversation_id=conversation_id
    )

    assert result["agent"] == "agent_b"
    assert result["intent"] == "travel_search"
    assert result["status"] == "completed"

    response = result["response"]

    assert response["search_category"] == "hotel"
    assert "Hotel Amrit Heritage Guest House" in response["formatted_message"]
    assert "Hotel Taposthali" in response["formatted_message"]

    assert conversation_id not in travel_search.travel_search_states

    print("TEST 1 PASSED: Hotel search and state cleanup")


# =====================================================
# 8. FLIGHT SEARCH TEST
# =====================================================

async def test_flight_search(conversation_id):

    result = await orchestrator.orchestrate(
        user_query="Find a flight from Varanasi to Delhi",
        conversation_id=conversation_id
    )

    assert result["agent"] == "agent_b"
    assert result["intent"] == "travel_search"
    assert result["status"] == "completed"

    response = result["response"]

    assert response["search_category"] == "flight"
    assert response["origin"]["airport_code"] == "VNS"
    assert response["destination"]["airport_code"] == "DEL"
    assert "IndiGo 6E 201" in response["formatted_message"]

    assert conversation_id not in travel_search.travel_search_states

    print("TEST 2 PASSED: Flight search and state cleanup")


# =====================================================
# 9. TRAIN SEARCH TEST
# =====================================================

async def test_train_search(conversation_id):

    result = await orchestrator.orchestrate(
        user_query="Find trains from Varanasi to Delhi",
        conversation_id=conversation_id
    )

    assert result["agent"] == "agent_b"
    assert result["intent"] == "travel_search"
    assert result["status"] == "completed"

    response = result["response"]

    assert response["search_category"] == "train"
    assert "Shiv Ganga Express" in response["formatted_message"]

    assert conversation_id not in travel_search.travel_search_states

    print("TEST 3 PASSED: Train search and automatic station resolution")


# =====================================================
# 10. CATEGORY SWITCH TEST
# =====================================================

async def test_category_switch(conversation_id):

    # First search: Hotels
    hotel_result = await orchestrator.orchestrate(
        user_query="Find hotels in Varanasi",
        conversation_id=conversation_id
    )

    assert hotel_result["status"] == "completed"
    assert hotel_result["response"]["search_category"] == "hotel"

    assert conversation_id not in travel_search.travel_search_states

    # Second search: Flights using the same conversation
    flight_result = await orchestrator.orchestrate(
        user_query="Find a flight from Varanasi to Delhi",
        conversation_id=conversation_id
    )

    assert flight_result["status"] == "completed"
    assert flight_result["response"]["search_category"] == "flight"

    assert "IndiGo 6E 201" in (
        flight_result["response"]["formatted_message"]
    )

    assert conversation_id not in travel_search.travel_search_states

    print("TEST 4 PASSED: Category switching in the same conversation")


# =====================================================
# 11. RUN ALL TESTS
# =====================================================

async def main():

    test_ids = [
        "end_to_end_hotel",
        "end_to_end_flight",
        "end_to_end_train",
        "end_to_end_category_switch"
    ]

    try:
        print("\n========================================")
        print("AGENT B END-TO-END TESTING")
        print("========================================")

        await test_hotel_search(test_ids[0])
        await test_flight_search(test_ids[1])
        await test_train_search(test_ids[2])
        await test_category_switch(test_ids[3])

        print("\n========================================")
        print("ALL AGENT B END-TO-END TESTS PASSED!")
        print("========================================")

    finally:
        for conversation_id in test_ids:
            travel_search.travel_search_states.pop(
                conversation_id, None
            )


if __name__ == "__main__":
    asyncio.run(main())
