import json
from pathlib import Path

from app.services.stayapi_service import search_hotels


def main():

    print("Searching live hotels in Varanasi...")

    results = search_hotels(
        dest_id=-2114217,
        dest_type="CITY",
        checkin="2026-11-25",
        checkout="2026-11-28",
        adults=2,
        rooms=1
    )

    # Save API response locally
    output_dir = Path("data/api_responses")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "varanasi_hotels_2026_11_25.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== HOTEL SEARCH SUMMARY ==========")

    print("Success:", results.get("success"))
    print("Message:", results.get("message"))

    data = results.get("data", {})

    print("Hotels found:", data.get("hotels_found"))
    print("Response saved:", output_file)

    print("\n========== HOTEL RESULTS ==========")

    for hotel in data.get("hotels", []):

        price = hotel.get("price") or {}

        print("\nHotel:", hotel.get("name"))
        print("Hotel ID:", hotel.get("hotel_id"))
        print("Price:", price.get("display"))
        rating = hotel.get("rating") or {}

        print("Star Rating:", hotel.get("star_rating"))
        print("Guest Rating:", rating.get("score"))
        print("Review Count:", rating.get("review_count"))
        print("Rating Description:", rating.get("display"))


if __name__ == "__main__":
    main()