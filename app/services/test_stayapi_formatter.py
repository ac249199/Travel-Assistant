import json

from pathlib import Path

from app.services.stayapi_service import (
    format_stayapi_hotels
)


def main():

    file_path = Path(
        "data/api_responses/varanasi_hotels_2026_11_25.json"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        results = json.load(file)

    hotels = format_stayapi_hotels(results)

    print("\n========== FORMATTED HOTEL RESULTS ==========")

    for hotel in hotels:

        print("\nHotel:", hotel["name"])
        print("Address:", hotel["address"])
        print("Price:", hotel["display_price"])
        print("Guest Rating:", hotel["guest_rating"])
        print("Reviews:", hotel["review_count"])
        print("Room:", hotel["room_name"])
        print("Free Cancellation:", hotel["free_cancellation"])
        print("No Prepayment:", hotel["no_prepayment"])
        print("Image:", hotel["image_url"])


if __name__ == "__main__":
    main()