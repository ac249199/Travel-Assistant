from datetime import date
from app.agents import travel_search


# --------------------------------------------------
# 1. MOCK RAILCORE STATION SEARCH
# --------------------------------------------------

def mock_resolve_train_station(query):

    stations = {
        "varanasi": [
            {
                "station_code": "BSB",
                "station_name": "Varanasi Junction",
                "display_name": "Varanasi Junction (BSB)",
                "city": "Varanasi",
                "confidence": 0.99
            },
            {
                "station_code": "BSBS",
                "station_name": "Banaras",
                "display_name": "Banaras (BSBS)",
                "city": "Varanasi",
                "confidence": 0.95
            }
        ],

        "delhi": [
            {
                "station_code": "NDLS",
                "station_name": "New Delhi",
                "display_name": "New Delhi (NDLS)",
                "city": "Delhi",
                "confidence": 0.99
            }
        ]
    }

    return {
        "query": query,
        "stations": stations.get(query.strip().lower(), [])
    }


# --------------------------------------------------
# 2. MOCK RAILCORE TRAIN SEARCH
# --------------------------------------------------

def mock_search_trains(
    from_station,
    to_station,
    journey_date,
    match="station"
):

    print("\nMOCK TRAIN API CALLED")

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
                    "classes": ["SL", "3A", "2A"],
                    "running_days": [
                        "MON", "TUE", "WED", "THU",
                        "FRI", "SAT", "SUN"
                    ]
                }
            ]
        }
    }


# --------------------------------------------------
# 3. REPLACE REAL API FUNCTIONS WITH MOCKS
# --------------------------------------------------

travel_search.resolve_train_station = mock_resolve_train_station
travel_search.search_trains = mock_search_trains


# --------------------------------------------------
# 4. MAIN TEST
# --------------------------------------------------

def test_train_selection_flow():

    conversation_id = "train_test_001"

    # Clear any previous test state
    travel_search.travel_search_states.pop(
        conversation_id,
        None
    )

    # Initial train search details
    travel_search.travel_search_states[conversation_id] = {

        "search_category": "train",

        "origin": "Varanasi",
        "destination": "Delhi",

        "journey_date": date(2026, 12, 10),

        "origin_station_code": None,
        "origin_station_name": None,

        "destination_station_code": None,
        "destination_station_name": None,

        "_pending_station_field": None,
        "_pending_station_candidates": []

    }

    # ----------------------------------------------
    # TEST 1: FIRST SEARCH
    # ----------------------------------------------

    print("\n========== TEST 1: FIRST SEARCH ==========")

    state = travel_search.travel_search_states[conversation_id]

    result = travel_search.execute_train_search(state)

    print("\nSearch result:")
    print(result)

    print("\nDEBUG - Current train state:")
    print(state)

    print(
        "\nDEBUG - Pending station field:",
        state.get("_pending_station_field")
    )

    print(
        "\nDEBUG - Pending candidates:",
        state.get("_pending_station_candidates")
    )

    assert result["status"] == "awaiting_station_selection"

    assert state.get("_pending_station_field"), (
        "Pending station field was not saved."
    )

    assert state.get("_pending_station_candidates"), (
        "Station candidates were not saved."
    )

    print("\nTEST 1 PASSED")

    # ----------------------------------------------
    # TEST 2: USER SELECTS VARANASI JUNCTION
    # ----------------------------------------------

    print("\n========== TEST 2: STATION SELECTION ==========")

    selection_result = travel_search.process_station_selection(
        "1",
        conversation_id
    )

    print("\nSelection result:")
    print(selection_result)

    state = travel_search.travel_search_states[conversation_id]

    print("\nUpdated state:")
    print(state)

    assert state.get("origin_station_code") == "BSB", (
        "Varanasi Junction was not selected correctly."
    )

    assert state.get("_pending_station_field") is None, (
        "Pending station field was not cleared."
    )

    print("\nTEST 2 PASSED")

    # ----------------------------------------------
    # TEST 3: TRAIN SEARCH AFTER SELECTION
    # ----------------------------------------------

    print("\n========== TEST 3: FINAL TRAIN SEARCH ==========")

    result = travel_search.execute_train_search(state)

    print("\nFinal search result:")
    print(result)

    assert result["status"] == "completed", (
        "Train search did not complete."
    )

    assert "Shiv Ganga Express" in result.get("formatted_message", ""), (
    "Expected train details were not found in the result."
    )

    print("\nTEST 3 PASSED")

    # ----------------------------------------------
    # FINAL RESULT
    # ----------------------------------------------

    print("\n======================================")
    print("ALL TRAIN SELECTION TESTS PASSED!")
    print("======================================")


# --------------------------------------------------
# 5. RUN TEST
# --------------------------------------------------

if __name__ == "__main__":

    test_train_selection_flow()
