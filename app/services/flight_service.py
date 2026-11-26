
import requests

from app.config import SERPAPI_API_KEY


SERPAPI_URL = "https://serpapi.com/search"


def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    adults: int = 1,
    travel_class: int = 1,
    currency: str = "INR",
    client=None
):
    """
    Search flights using SerpApi Google Flights.

    travel_class:
    1 = Economy
    2 = Premium Economy
    3 = Business
    4 = First Class
    """

    if not SERPAPI_API_KEY:
        raise ValueError("SERPAPI_API_KEY is missing.")

    if adults < 1:
        raise ValueError("At least one adult is required.")

    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "adults": adults,
        "travel_class": travel_class,
        "currency": currency,
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_API_KEY
    }

    if return_date:
        params["type"] = "1"
        params["return_date"] = return_date
    else:
        params["type"] = "2"

    http_client = client or requests

    response = http_client.get(
        SERPAPI_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data


def format_flight_results(data: dict) -> str:
    """Convert flight search results into readable text."""

    flights = (
        data.get("best_flights", [])
        + data.get("other_flights", [])
    )

    if not flights:
        return "No flights found for the selected journey."

    results = []

    for index, flight in enumerate(flights[:10], start=1):
        segments = flight.get("flights", [])

        if not segments:
            continue

        first = segments[0]
        last = segments[-1]

        airline = first.get("airline", "Unknown airline")
        flight_number = first.get("flight_number", "")
        departure = first.get("departure_airport", {})
        arrival = last.get("arrival_airport", {})

        results.append(
            f"{index}. {airline} {flight_number}\n"
            f"   From: {departure.get('name', '')} "
            f"({departure.get('id', '')})\n"
            f"   Departure: {departure.get('time', '')}\n"
            f"   To: {arrival.get('name', '')} "
            f"({arrival.get('id', '')})\n"
            f"   Arrival: {arrival.get('time', '')}\n"
            f"   Duration: {flight.get('total_duration', 'N/A')} minutes\n"
            f"   Price: {flight.get('price', 'N/A')} {data.get('search_parameters', {}).get('currency', 'INR')}"
        )

    return "\n\n".join(results) if results else (
        "Flight results were returned, but no usable flight details were found."
    )
