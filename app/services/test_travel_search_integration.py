
import asyncio
from datetime import date
from types import SimpleNamespace

from app.orchestration import orchestrator
from app.agents import agent_b
from app.agents import travel_search


# =====================================================
# 1. MOCK INTENT CLASSIFIER
# =====================================================

def mock_classify_intent(user_query):

    return SimpleNamespace(
        intent="travel_search",
        target_agent="agent_b",
        clarification_needed=False,
        missing_information=[]
    )


# =====================================================
# 2. MOCK AGENT B WORKFLOW ROUTER
# =====================================================

def mock_route_agent_b(user_query):

    return SimpleNamespace(
        workflow="travel_search"
    )


# =====================================================
# 3. MOCK TRAVEL SEARCH EXTRACTION
# =====================================================

def mock_collect_travel_search_details(
    user_query,
    conversation_id
):

    if "hotel" in user_query.lower():

        state = {
            "search_category": "hotel",
            "destination": "Varanasi",
            "check_in_date": date(2026, 11, 25),
            "check_out_date": date(2026, 11, 27),
            "guests": 2,
            "budget_per_night": None,
            "preferences": []
        }

    elif "flight" in user_query.lower():

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

    else:

        return {
            "status": "error",
            "message": "Unsupported test request."
        }

    travel_search.travel_search_states[
        conversation_id
    ] = state

    return {
        "status": "ready_to_search",
        "search_request": state
    }


# =====================================================
# 4. MOCK STAYAPI SERVICES
# =====================================================

def mock_get_stayapi_destination(destination):

    print("\nMOCK STAYAPI DESTINATION LOOKUP")

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

    print("\nMOCK STAYAPI HOTEL SEARCH")

    print("Destination:", dest_id)
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
# 5. MOCK AIRPORT RESOLUTION
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


# =====================================================
# 6. MOCK SERPAPI FLIGHT SEARCH
# =====================================================

def mock_search_flights(
    departure_id,
    arrival_id,
    outbound_date,
    return_date=None,
    adults=1,
    travel_class=1
):

    print("\nMOCK SERPAPI FLIGHT SEARCH")

    print("From:", departure_id)
    print("To:", arrival_id)
    print("Departure:", outbound_date)
    print("Return:", return_date)
    print("Adults:", adults)
    print("Class:", travel_class)

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
# 7. APPLY ALL MOCKS
# =====================================================

orchestrator.classify_intent = mock_classify_intent

agent_b.route_agent_b = mock_route_agent_b

travel_search.collect_travel_search_details = (
    mock_collect_travel_search_details
)

# StayAPI mocks
travel_search.get_stayapi_destination = (
    mock_get_stayapi_destination
)

travel_search.search_hotels = mock_search_hotels

travel_search.format_stayapi_hotels = (
    mock_format_stayapi_hotels
)

# Flight mocks
travel_search.resolve_airport = mock_resolve_airport

travel_search.search_flights = mock_search_flights

travel_search.format_flight_results = (
    mock_format_flight_results
)


# =====================================================
# 8. HOTEL INTEGRATION TEST
# =====================================================

async def test_hotel_search():

    conversation_id = "hotel_integration_test"

    print("\n====================================")
    print("HOTEL SEARCH INTEGRATION TEST")
    print("====================================")

    result = await orchestrator.orchestrate(

        user_query=(
            "Find hotels in Varanasi "
            "from 25 November 2026 "
            "to 27 November 2026 "
            "for 2 guests"
        ),

        conversation_id=conversation_id
    )

    print("\nHOTEL RESULT:")
    print(result)

    assert result["agent"] == "agent_b"

    assert result["intent"] == "travel_search"

    assert result["status"] == "completed"

    response = result["response"]

    assert response["search_category"] == "hotel"

    assert "Hotel Amrit Heritage Guest House" in (
        response["formatted_message"]
    )

    assert "Hotel Taposthali" in (
        response["formatted_message"]
    )

    assert conversation_id not in (
        travel_search.travel_search_states
    )

    print("\nHOTEL SEARCH TEST PASSED!")


# =====================================================
# 9. FLIGHT INTEGRATION TEST
# =====================================================

async def test_flight_search():

    conversation_id = "flight_integration_test"

    print("\n====================================")
    print("FLIGHT SEARCH INTEGRATION TEST")
    print("====================================")

    result = await orchestrator.orchestrate(

        user_query=(
            "Find a one-way flight "
            "from Varanasi to Delhi "
            "on 10 December 2026 "
            "for 1 adult in economy"
        ),

        conversation_id=conversation_id
    )

    print("\nFLIGHT RESULT:")
    print(result)

    assert result["agent"] == "agent_b"

    assert result["intent"] == "travel_search"

    assert result["status"] == "completed"

    response = result["response"]

    assert response["search_category"] == "flight"

    assert response["origin"]["airport_code"] == "VNS"

    assert response["destination"]["airport_code"] == "DEL"

    assert "IndiGo 6E 201" in (
        response["formatted_message"]
    )

    assert conversation_id not in (
        travel_search.travel_search_states
    )

    print("\nFLIGHT SEARCH TEST PASSED!")


# =====================================================
# 10. RUN BOTH TESTS
# =====================================================

async def main():

    await test_hotel_search()

    await test_flight_search()

    print("\n====================================")
    print("ALL HOTEL AND FLIGHT TESTS PASSED!")
    print("====================================")


if __name__ == "__main__":

    asyncio.run(main())
