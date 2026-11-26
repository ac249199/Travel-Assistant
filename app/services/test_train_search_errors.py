
from unittest.mock import Mock, patch
from datetime import date
from pydantic import ValidationError

from app.services import train_service
from app.agents import travel_search
from app.schemas.travel_search_extraction_schema import TravelSearchExtraction


def test_station_not_found():
    """Test station search when no station matches."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"results": []}
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(train_service.requests, "get", return_value=mock_response):
        result = train_service.search_stations("UnknownStation")

    assert result["data"]["results"] == []
    print("TEST 1 PASSED: Station not found")


def test_invalid_station_selection():
    """Test when the user selects a number outside the available options."""
    candidates = [
        {
            "station_code": "BSB",
            "station_name": "Varanasi Junction",
            "display_name": "Varanasi Junction (BSB)"
        }
    ]

    result = travel_search.match_station_selection("9", candidates)

    assert result is None
    print("TEST 2 PASSED: Invalid station selection")


def test_no_trains_available():
    """Test a successful API response with no trains."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"trains": []}
    }
    mock_response.raise_for_status.return_value = None

    with patch.object(train_service.requests, "get", return_value=mock_response):
        result = train_service.search_trains(
            from_station="BSB",
            to_station="NDLS",
            journey_date="2026-12-10"
        )

    assert result["data"]["trains"] == []
    print("TEST 3 PASSED: No trains available")


def test_railcore_server_error():
    """Test handling of an HTTP server error."""
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = train_service.requests.HTTPError(
        "500 Server Error"
    )

    with patch.object(train_service.requests, "get", return_value=mock_response):
        try:
            train_service.search_trains(
                from_station="BSB",
                to_station="NDLS",
                journey_date="2026-12-10"
            )
            assert False, "Expected HTTPError was not raised"
        except train_service.requests.HTTPError:
            pass

    print("TEST 4 PASSED: RailCore server error")


def test_railcore_timeout():
    """Test handling of an API timeout."""
    with patch.object(
        train_service.requests,
        "get",
        side_effect=train_service.requests.Timeout("Mock timeout")
    ):
        try:
            train_service.search_trains(
                from_station="BSB",
                to_station="NDLS",
                journey_date="2026-12-10"
            )
            assert False, "Expected Timeout was not raised"
        except train_service.requests.Timeout:
            pass

    print("TEST 5 PASSED: RailCore timeout")


def test_invalid_journey_date():
    """Test schema validation for an invalid journey date."""
    try:
        TravelSearchExtraction(
            search_category="train",
            journey_date="not-a-valid-date"
        )
        assert False, "Expected date validation error was not raised"
    except ValidationError:
        pass

    print("TEST 6 PASSED: Invalid journey date")


def run_tests():
    tests = [
        test_station_not_found,
        test_invalid_station_selection,
        test_no_trains_available,
        test_railcore_server_error,
        test_railcore_timeout,
        test_invalid_journey_date
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print("\n" + "=" * 45)
    print(f"TRAIN SEARCH ERROR TESTS: {passed}/{len(tests)} PASSED")
    print("=" * 45)


if __name__ == "__main__":
    run_tests()
