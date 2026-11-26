
import requests

from app.config import RAILCORE_API_KEY


RAILCORE_BASE_URL = "https://ir.railcore.tech/v1"


def get_headers():
    if not RAILCORE_API_KEY:
        raise ValueError("RAILCORE_API_KEY is missing.")

    return {
        "X-RailCore-Key": RAILCORE_API_KEY
    }


def search_stations(query: str, limit: int = 5):
    """Find railway stations by city, name or station code."""

    response = requests.get(
        f"{RAILCORE_BASE_URL}/stations/search",
        headers=get_headers(),
        params={"q": query, "limit": limit},
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise RuntimeError(data.get("error", "Station search failed"))

    return data


def search_trains(
    from_station: str,
    to_station: str,
    journey_date: str,
    match: str = "station"
):
    """Search trains between two station codes."""

    response = requests.get(
        f"{RAILCORE_BASE_URL}/journeys/search",
        headers=get_headers(),
        params={
            "from": from_station,
            "to": to_station,
            "date": journey_date,
            "match": match
        },
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise RuntimeError(data.get("error", "Train search failed"))

    return data



def format_train_results(data: dict) -> str:
    """Format RailCore journey results."""

    payload = data.get("data", data)
    trains = payload.get("trains", [])

    if not trains:
        return "No trains found for the selected journey."

    results = []

    for index, train in enumerate(trains[:10], start=1):

        train_name = train.get(
            "extended_train_name",
            train.get("train_name", "Unknown train")
        )

        train_number = train.get("train_number", "N/A")

        origin = train.get("from_station_name", "Unknown station")
        origin_code = train.get("from_station_code")

        destination = train.get("to_station_name", "Unknown station")
        destination_code = train.get("to_station_code")

        # Avoid displaying empty parentheses
        origin_display = (
            f"{origin} ({origin_code})"
            if origin_code else origin
        )

        destination_display = (
            f"{destination} ({destination_code})"
            if destination_code else destination
        )

        departure = train.get("departure_time", "N/A")
        arrival = train.get("arrival_time", "N/A")

        duration = train.get("duration_minutes")

        if duration is not None:
            hours, minutes = divmod(duration, 60)
            duration = f"{hours}h {minutes}m"
        else:
            duration = "N/A"

        classes = train.get("classes", [])
        running_days = train.get("running_days", [])

        results.append(
            f"{index}. {train_name} ({train_number})\n"
            f"   From: {origin_display}\n"
            f"   Departure: {departure}\n"
            f"   To: {destination_display}\n"
            f"   Arrival: {arrival}\n"
            f"   Duration: {duration}\n"
            f"   Classes: {', '.join(classes) if classes else 'N/A'}\n"
            f"   Running days: {', '.join(running_days) if running_days else 'N/A'}"
        )

    return "\n\n".join(results)


# =========================================================
# STATION SEARCH CACHE
# =========================================================

station_search_cache = {}


def resolve_train_station(query: str):
    """
    Find railway stations using RailCore.

    Cached searches avoid repeated API requests.
    Multiple possible stations are returned for user selection.
    """

    normalized_query = query.strip().lower()

    if not normalized_query:
        raise ValueError("Station search query cannot be empty.")

    # Reuse cached station results
    if normalized_query in station_search_cache:
        print("Using cached station results:", query)
        return station_search_cache[normalized_query]

    # Search RailCore
    response = search_stations(
        query=query,
        limit=5
    )

    if not response.get("success"):
        raise RuntimeError(
            response.get("error", "Station search failed.")
        )

    results = response.get("data", {}).get("results", [])

    stations = []

    for station in results:

        stations.append({
            "station_code": station.get("station_code"),
            "station_name": station.get("station_name"),
            "display_name": station.get("display_name"),
            "city": station.get("city"),
            "state": station.get("state"),
            "confidence": station.get("confidence")
        })

    result = {
        "query": query,
        "stations": stations
    }

    station_search_cache[normalized_query] = result

    return result
