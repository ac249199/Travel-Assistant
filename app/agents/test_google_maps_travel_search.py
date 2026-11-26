
import asyncio

from app.agents.travel_search import search_travel_places

from app.agents.travel_search import (
    search_travel_places,
    format_travel_search_results
)

async def main():

    search_request = {
        "search_category": "hotel",
        "destination": "Varanasi",
        "origin": None,
        "check_in_date": None,
        "check_out_date": None,
        "guests": 2,
        "budget_per_night": None,
        "preferences": ["budget"]
    }

    results = await search_travel_places(search_request)

    formatted_results = format_travel_search_results(results)

    print("\n========== FORMATTED RESULTS ==========")

    for hotel in formatted_results:
        print("\nHotel Name:", hotel["name"])
        print("Place ID:", hotel["place_id"])
        print("Rating:", hotel["rating"])
        print("Reviews:", hotel["reviews"])
        print("Description:", hotel["description"])
        print("Google Maps:", hotel["google_maps_url"])
        print("Directions:", hotel["directions_url"])


if __name__ == "__main__":
    asyncio.run(main())
