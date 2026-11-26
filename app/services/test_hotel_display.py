
import json

from app.services.stayapi_service import format_stayapi_hotels

from app.agents.travel_search import format_hotel_results_for_user


def main():

    # Load previously saved StayAPI response
    file_path = "data/api_responses/varanasi_hotels_2026_11_25.json"

    with open(file_path, "r", encoding="utf-8") as file:
        raw_results = json.load(file)

    # Format raw API hotel data
    hotels = format_stayapi_hotels(raw_results)

    # Prepare search result
    search_result = {
        "status": "completed",
        "destination": "Varanasi",
        "check_in_date": "2026-11-25",
        "check_out_date": "2026-11-28",
        "guests": 2,
        "hotels": hotels
    }

    # Generate readable response
    formatted_message = format_hotel_results_for_user(
        search_result
    )

    print("\n========== FORMATTED HOTEL RESULTS ==========\n")

    print(formatted_message)

    assert len(hotels) > 0
    assert "Hotel Amrit Heritage Guest House" in formatted_message
    assert "Free cancellation" in formatted_message

    print("\nHotel formatter test passed!")


if __name__ == "__main__":
    main()
