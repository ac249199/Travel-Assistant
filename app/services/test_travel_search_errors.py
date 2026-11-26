
import asyncio
from datetime import date
from types import SimpleNamespace

from app.orchestration import orchestrator
from app.agents import agent_b
from app.agents import travel_search
from app.schemas.travel_search_extraction_schema import TravelSearchExtraction


# =====================================================
# 1. MOCK CLASSIFICATION AND ROUTING
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


orchestrator.classify_intent = mock_classify_intent
agent_b.route_agent_b = mock_route_agent_b


# =====================================================
# 2. MOCK EXTRACTION
# =====================================================

class MockExtractionChain:

    def __init__(self, extraction):
        self.extraction = extraction

    def invoke(self, payload):
        return self.extraction


def set_extraction(extraction):
    travel_search.travel_search_extraction_chain = (
        MockExtractionChain(extraction)
    )


# =====================================================
# 3. HOTEL MOCKS
# =====================================================

def mock_destination_success(destination):
    return {
        "success": True,
        "dest_id": "-2114217",
        "dest_type": "CITY"
    }


def mock_destination_failure(destination):
    return {
        "success": False,
        "message": "Destination not found."
    }


def mock_hotel_search_empty(**kwargs):
    return {
        "success": True,
        "hotels": []
    }


def mock_hotel_search_error(**kwargs):
    raise RuntimeError("Mock StayAPI server error")


def mock_hotel_search_timeout(**kwargs):
    raise TimeoutError("Mock StayAPI request timed out")


def mock_format_empty_hotels(results):
    return []


# =====================================================
# 4. FLIGHT MOCKS
# =====================================================

def mock_airport_failure(city):
    return {
        "success": False,
        "message": f"Airport could not be identified for {city}."
    }


def mock_airport_success(city):
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


def mock_flight_search_empty(**kwargs):
    return {
        "best_flights": [],
        "other_flights": []
    }


# =====================================================
# 5. HELPER TO CREATE TEST REQUESTS
# =====================================================

def hotel_extraction(
    checkin=date(2026, 12, 10),
    checkout=date(2026, 12, 12)
):

    return TravelSearchExtraction(
        search_category="hotel",
        destination="Varanasi",
        check_in_date=checkin,
        check_out_date=checkout,
        guests=2
    )


def flight_extraction(origin="Varanasi", destination="Delhi"):

    return TravelSearchExtraction(
        search_category="flight",
        origin=origin,
        destination=destination,
        departure_date=date(2026, 12, 10),
        trip_type="one_way",
        adults=1,
        travel_class=1
    )


# =====================================================
# 6. TEST 1: INVALID HOTEL DATES
# =====================================================

async def test_invalid_hotel_dates():

    print("\n========== TEST 1: INVALID HOTEL DATES ==========")

    set_extraction(
        hotel_extraction(
            checkin=date(2026, 12, 15),
            checkout=date(2026, 12, 12)
        )
    )

    conversation_id = "error_hotel_dates"

    result = await orchestrator.orchestrate(
        "Find a hotel in Varanasi",
        conversation_id
    )

    print(result)

    assert result["status"] == "awaiting_information"

    assert "Check-out date must be after check-in date" in (
        result["response"]["message"]
    )

    print("TEST 1 PASSED")


# =====================================================
# 7. TEST 2: DESTINATION NOT FOUND
# =====================================================

async def test_hotel_destination_not_found():

    print("\n========== TEST 2: DESTINATION NOT FOUND ==========")

    set_extraction(hotel_extraction())

    travel_search.get_stayapi_destination = (
        mock_destination_failure
    )

    conversation_id = "error_hotel_destination"

    result = await orchestrator.orchestrate(
        "Find hotels in Varanasi",
        conversation_id
    )

    print(result)

    assert result["status"] == "error"

    assert "Unable to identify" in (
        result["response"]["message"]
    )

    print("TEST 2 PASSED")


# =====================================================
# 8. TEST 3: NO HOTELS AVAILABLE
# =====================================================

async def test_no_hotels_found():

    print("\n========== TEST 3: NO HOTELS FOUND ==========")

    set_extraction(hotel_extraction())

    travel_search.get_stayapi_destination = (
        mock_destination_success
    )

    travel_search.search_hotels = mock_hotel_search_empty

    travel_search.format_stayapi_hotels = (
        mock_format_empty_hotels
    )

    conversation_id = "error_no_hotels"

    result = await orchestrator.orchestrate(
        "Find hotels in Varanasi",
        conversation_id
    )

    print(result)

    assert result["status"] == "completed"

    assert "No hotels were found" in (
        result["response"]["formatted_message"]
    )

    print("TEST 3 PASSED")


# =====================================================
# 9. TEST 4: UNSUPPORTED AIRPORT
# =====================================================

async def test_unsupported_airport():

    print("\n========== TEST 4: UNSUPPORTED AIRPORT ==========")

    set_extraction(
        flight_extraction(
            origin="Unknown City",
            destination="Delhi"
        )
    )

    travel_search.resolve_airport = mock_airport_failure

    conversation_id = "error_unsupported_airport"

    result = await orchestrator.orchestrate(
        "Find a flight from an unknown city to Delhi",
        conversation_id
    )

    print(result)

    assert result["status"] == "error"

    assert "Airport could not be identified" in (
        result["response"]["message"]
    )

    print("TEST 4 PASSED")


# =====================================================
# 10. TEST 5: NO FLIGHTS AVAILABLE
# =====================================================

async def test_no_flights_found():

    print("\n========== TEST 5: NO FLIGHTS FOUND ==========")

    set_extraction(flight_extraction())

    travel_search.resolve_airport = mock_airport_success

    travel_search.search_flights = mock_flight_search_empty

    conversation_id = "error_no_flights"

    result = await orchestrator.orchestrate(
        "Find a flight from Varanasi to Delhi",
        conversation_id
    )

    print(result)

    assert result["status"] == "completed"

    assert "No flights found" in (
        result["response"]["formatted_message"]
    )

    print("TEST 5 PASSED")


# =====================================================
# 11. TEST 6: HOTEL API ERROR
# =====================================================

async def test_hotel_api_error():

    print("\n========== TEST 6: HOTEL API ERROR ==========")

    set_extraction(hotel_extraction())

    travel_search.get_stayapi_destination = (
        mock_destination_success
    )

    travel_search.search_hotels = mock_hotel_search_error

    conversation_id = "error_hotel_api"

    result = await orchestrator.orchestrate(
        "Find hotels in Varanasi",
        conversation_id
    )

    print(result)

    assert result["status"] == "error"

    assert "Something went wrong" in (
        result["response"]["message"]
    )

    print("TEST 6 PASSED")


# =====================================================
# 12. TEST 7: HOTEL API TIMEOUT
# =====================================================

async def test_hotel_api_timeout():

    print("\n========== TEST 7: HOTEL API TIMEOUT ==========")

    set_extraction(hotel_extraction())

    travel_search.get_stayapi_destination = (
        mock_destination_success
    )

    travel_search.search_hotels = mock_hotel_search_timeout

    conversation_id = "error_hotel_timeout"

    result = await orchestrator.orchestrate(
        "Find hotels in Varanasi",
        conversation_id
    )

    print(result)

    assert result["status"] == "error"

    assert "Something went wrong" in (
        result["response"]["message"]
    )

    print("TEST 7 PASSED")


# =====================================================
# 13. RUN ALL TESTS
# =====================================================

async def main():

    tests = [
        test_invalid_hotel_dates,
        test_hotel_destination_not_found,
        test_no_hotels_found,
        test_unsupported_airport,
        test_no_flights_found,
        test_hotel_api_error,
        test_hotel_api_timeout
    ]

    passed = 0

    for test in tests:

        try:
            await test()
            passed += 1

        except Exception as error:

            print("\nTEST FAILED:", test.__name__)
            print("Error:", str(error))

            raise

        finally:

            # Prevent state leaking between tests
            for conversation_id in list(
                travel_search.travel_search_states
            ):
                if conversation_id.startswith("error_"):
                    travel_search.travel_search_states.pop(
                        conversation_id,
                        None
                    )

    print("\n====================================")
    print(f"ERROR HANDLING TESTS: {passed}/{len(tests)} PASSED")
    print("====================================")


if __name__ == "__main__":

    asyncio.run(main())
