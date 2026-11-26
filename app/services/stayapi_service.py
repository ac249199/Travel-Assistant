import requests

from app.config import STAYAPI_API_KEY

STAYAPI_BASE_URL = "https://api.stayapi.com"


def lookup_destination(destination: str):

    url = f"{STAYAPI_BASE_URL}/v1/booking/destinations/lookup"

    headers = {
        "x-api-key": STAYAPI_API_KEY
    }

    params = {
        "query": destination
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def search_hotels(
    dest_id: int,
    dest_type: str,
    checkin: str,
    checkout: str,
    adults: int = 2,
    rooms: int = 1
):

    url = f"{STAYAPI_BASE_URL}/v1/booking/search"

    headers = {
        "x-api-key": STAYAPI_API_KEY
    }

    params = {
        "dest_id": dest_id,
        "dest_type": dest_type,
        "checkin": checkin,
        "checkout": checkout,
        "adults": adults,
        "rooms": rooms,
        "rows_per_page": 5,
        "currency": "INR",
        "market": "IN",
        "language": "en"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json()

def format_stayapi_hotels(results: dict):

    data = results.get("data", {})
    hotels = data.get("hotels", [])

    formatted_hotels = []

    for hotel in hotels:

        price = hotel.get("price") or {}
        rating = hotel.get("rating") or {}

        formatted_hotel = {
            "hotel_id": hotel.get("hotel_id"),
            "name": hotel.get("name"),
            "address": hotel.get("address"),
            "city": hotel.get("city"),
            "distance": hotel.get("distance"),

            "price": price.get("amount"),
            "currency": price.get("currency"),
            "display_price": price.get("display"),
            "original_price": price.get("before_discount"),

            "star_rating": hotel.get("star_rating"),
            "guest_rating": rating.get("score"),
            "review_count": rating.get("review_count"),

            "image_url": hotel.get("image_url"),
            "room_name": hotel.get("room_name"),

            "free_cancellation": hotel.get("free_cancellation"),
            "no_prepayment": hotel.get("no_prepayment"),
            "is_sold_out": hotel.get("is_sold_out")
        }

        formatted_hotels.append(formatted_hotel)

    return formatted_hotels