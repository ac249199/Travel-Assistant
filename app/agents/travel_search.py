
import json
import re
from datetime import date, datetime
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_service import get_llm

from app.services.stayapi_service import (
    lookup_destination,
    search_hotels,
    format_stayapi_hotels
)

from app.services.flight_service import (
    search_flights,
    format_flight_results
)

from app.services.train_service import (
    search_stations,
    search_trains,
    format_train_results,
    resolve_train_station
)

from app.services.airport_service import resolve_airport

from app.schemas.travel_search_extraction_schema import (
    TravelSearchExtraction
)


# =========================================================
# 1. INITIALIZE LLM
# =========================================================

llm = get_llm()

travel_search_llm = llm.with_structured_output(
    TravelSearchExtraction
)


# =========================================================
# 2. CONVERSATION STATE
# =========================================================

travel_search_states = {}

# Stores the latest completed search results
# for each conversation.
travel_search_results = {}


# =========================================================
# 3. TRAVEL OPTION SELECTION
# =========================================================

def select_travel_option(
    conversation_id: str,
    user_query: str
):

    search_result = travel_search_results.get(
        conversation_id
    )

    if not search_result:
        return {
            "status": "error",
            "message": "No previous travel search results found."
        }

    category = search_result.get("search_category")

    # Get options based on search category
    if category == "hotel":
        options = search_result.get("hotels", [])

    elif category == "flight":
        options = search_result.get("flights", [])

    elif category == "train":
        options = search_result.get("trains", [])

    else:
        return {
            "status": "error",
            "message": "Unsupported travel service."
        }

    if not options:
        return {
            "status": "error",
            "message": "No selectable options are available."
        }

    query = user_query.strip().lower()

    # Match numerical selection
    number_match = re.search(
        r"\b(?:option|number|no\.?|choice)?\s*(\d+)\b",
        query
    )

    selected_option = None
    selected_index = None

    if number_match:

        index = int(number_match.group(1)) - 1

        if 0 <= index < len(options):
            selected_option = options[index]
            selected_index = index + 1

    # Match by service name if no valid number was selected
    if selected_option is None:

        for index, option in enumerate(options):

            if category == "hotel":

                searchable_text = option.get("name", "")

            elif category == "flight":

                segments = option.get("flights", [])

                searchable_text = " ".join([
                    str(segments[0].get("airline", "")),
                    str(segments[0].get("flight_number", ""))
                ]) if segments else ""

            else:

                searchable_text = " ".join([
                    str(option.get("extended_train_name", "")),
                    str(option.get("train_name", "")),
                    str(option.get("train_number", ""))
                ])

            if query and query in searchable_text.lower():

                selected_option = option
                selected_index = index + 1
                break

    if selected_option is None:

        return {
            "status": "selection_not_found",
            "message": (
                "I couldn't identify that option. "
                "Please select a valid option number or name."
            )
        }

    return {
        "status": "selected",
        "search_category": category,
        "selection_number": selected_index,
        "selected_option": selected_option
    }



# =========================================================
# 3. EXTRACTION PROMPT
# =========================================================

travel_search_extraction_prompt = ChatPromptTemplate.from_messages([

    ("system", """
    You extract travel-search details for Banarasi Bhaukal Travel Guru.

    The application provides the EXISTING SEARCH STATE and the LATEST USER MESSAGE.
    Use the existing state only to understand the active category and interpret short
    follow-ups. Extract only details newly stated or clearly corrected in the latest
    message. Do not copy existing values into the extraction output.

    SUPPORTED CATEGORIES: hotel, flight, train.

    COMMON: search_category, destination, origin, preferences.
    HOTEL: check_in_date, check_out_date, guests, budget_per_night.
    In an active hotel search, "2 adults" or "2 people" means guests=2.
    FLIGHT: departure_date, return_date, trip_type, adults, children, infants,
    travel_class. In an active flight search, a date-only follow-up means
    departure_date unless the user explicitly says it is the return date.
    "One way" means trip_type=one_way; "round trip" or "return flight" means
    trip_type=round_trip. Passenger counts map to adults/children/infants.
    Flight class: Economy=1, Premium Economy=2, Business=3, First Class=4.
    TRAIN: journey_date, train_class, quota. In an active train search, a date-only
    follow-up means journey_date.

    RULES:
    - Do not invent missing details or assume dates, cities, passengers or preferences.
    - Accommodation searches map to hotel; air-ticket searches map to flight;
      railway searches map to train.
    - Do not classify restaurants, sightseeing or local transport as travel search.
    - Flight trip_type must be one_way or round_trip; do not assume one-way unless
      the user indicates it.
    - Preserve station and city names as stated.
    - Return null for fields not newly provided in the latest message.
    - Extract preferences only when the latest message provides them.
    """),

    ("human", """
    EXISTING SEARCH STATE (context only; do not copy its values as newly extracted):
    {current_search_state}

    LATEST USER MESSAGE:
    {user_query}
    """)

])


travel_search_extraction_chain = (
    travel_search_extraction_prompt | travel_search_llm
)


# =========================================================
# 3A. DETERMINISTIC DATE EXTRACTION
# =========================================================

MONTH_PATTERN = (
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December|Jan|Feb|Mar|Apr|"
    r"Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)

DATE_PATTERNS = [
    rf"\b\d{{1,2}}\s+(?:{MONTH_PATTERN})\.?,?\s+\d{{4}}\b",
    rf"\b(?:{MONTH_PATTERN})\.?\s+\d{{1,2}},?\s+\d{{4}}\b",
    r"\b\d{4}-\d{1,2}-\d{1,2}\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
]


def extract_explicit_dates(user_query: str) -> list[date]:
    """Extract explicitly written dates from the latest user message."""

    matches = []
    for pattern in DATE_PATTERNS:
        matches.extend(
            re.finditer(pattern, user_query, flags=re.IGNORECASE)
        )

    matches.sort(key=lambda match: match.start())

    formats = [
        "%d %B %Y", "%d %b %Y",
        "%B %d %Y", "%b %d %Y",
        "%Y-%m-%d",
        "%d/%m/%Y", "%d-%m-%Y",
    ]

    extracted_dates = []
    last_end = -1

    for match in matches:
        if match.start() < last_end:
            continue

        raw_value = match.group(0).replace(",", "").replace(".", "")
        parsed_date = None

        for date_format in formats:
            try:
                parsed_date = datetime.strptime(
                    raw_value, date_format
                ).date()
                break
            except ValueError:
                continue

        if parsed_date is not None:
            extracted_dates.append(parsed_date)
            last_end = match.end()

    return list(dict.fromkeys(extracted_dates))


def apply_deterministic_dates(
    search_state: dict,
    user_query: str
) -> None:
    """Use deterministic dates to override unreliable LLM date parsing."""

    dates = extract_explicit_dates(user_query)
    if not dates:
        return

    category = search_state.get("search_category")
    query_lower = user_query.lower()

    if category == "hotel":
        search_state["check_in_date"] = dates[0]
        if len(dates) >= 2:
            search_state["check_out_date"] = dates[1]

    elif category == "flight":
        if "return" in query_lower:
            search_state["return_date"] = dates[0]
        else:
            search_state["departure_date"] = dates[0]
            if len(dates) >= 2:
                search_state["return_date"] = dates[1]

    elif category == "train":
        search_state["journey_date"] = dates[0]


# =========================================================
# 4. INITIALIZE SEARCH STATE
# =========================================================

def create_search_state():

    return {

        "search_category": None,
        "destination": None,
        "origin": None,

        # Hotel
        "check_in_date": None,
        "check_out_date": None,
        "guests": None,
        "budget_per_night": None,

        # Flight
        "departure_date": None,
        "return_date": None,
        "trip_type": None,
        "adults": None,
        "children": 0,
        "infants": 0,
        "travel_class": None,

        # Train
        "journey_date": None,
        "train_class": None,
        "quota": None,

        # Resolved train stations
        "origin_station_code": None,
        "origin_station_name": None,
        "destination_station_code": None,
        "destination_station_name": None,

        # Pending station selection
        "_pending_station_field": None,
        "_pending_station_candidates": [],

        "preferences": []

    }


# =========================================================
# 5. IDENTIFY MISSING INFORMATION
# =========================================================

def get_missing_search_information(search_state):

    missing_information = []

    category = search_state["search_category"]

    if not category:
        return ["search category"]

    # HOTEL
    if category == "hotel":

        if not search_state["destination"]:
            missing_information.append("destination")

        if not search_state["check_in_date"]:
            missing_information.append("check-in date")

        if not search_state["check_out_date"]:
            missing_information.append("check-out date")

        if not search_state["guests"]:
            missing_information.append("number of guests")

    # FLIGHT
    elif category == "flight":

        if not search_state["origin"]:
            missing_information.append("departure city")

        if not search_state["destination"]:
            missing_information.append("arrival city")

        if not search_state["departure_date"]:
            missing_information.append("departure date")

        if not search_state["trip_type"]:
            missing_information.append("trip type")

        if (
            search_state["trip_type"] == "round_trip"
            and not search_state["return_date"]
        ):
            missing_information.append("return date")

    # TRAIN
    elif category == "train":

        if not search_state["origin"]:
            missing_information.append(
                "departure station or city"
            )

        if not search_state["destination"]:
            missing_information.append(
                "arrival station or city"
            )

        if not search_state["journey_date"]:
            missing_information.append("journey date")

    return missing_information


# =========================================================
# 6. GENERATE FOLLOW-UP QUESTIONS
# =========================================================

def generate_search_followup(missing_information):

    questions = {

        "search category":
            "Would you like to search for hotels, flights or trains?",

        "destination":
            "Which destination would you like to search in?",

        "check-in date":
            "What is your hotel check-in date?",

        "check-out date":
            "What is your hotel check-out date?",

        "number of guests":
            "How many guests will be staying?",

        "departure city":
            "Which city or airport will you depart from?",

        "arrival city":
            "Which city or airport are you travelling to?",

        "departure date":
            "What is your flight departure date?",

        "trip type":
            "Is this a one-way or round-trip flight?",

        "return date":
            "What is your return flight date?",

        "departure station or city":
            "Which railway station or city will you depart from?",

        "arrival station or city":
            "Which railway station or city are you travelling to?",

        "journey date":
            "What is your train journey date?"

    }

    followup_questions = [
        questions[item]
        for item in missing_information
    ]

    return (
        "I need a little more information:\n"
        + "\n".join(followup_questions)
    )


# =========================================================
# 7. COLLECT SEARCH DETAILS
# =========================================================

def collect_travel_search_details(
    user_query: str,
    conversation_id: str
):

    search_state = travel_search_states.get(
        conversation_id
    )

    if search_state is None:

        search_state = create_search_state()

        travel_search_states[conversation_id] = search_state

    extracted_details = travel_search_extraction_chain.invoke({

        "user_query": user_query,
        "current_search_state": str(search_state)

    })

    print("\nExtracted Search Details:", extracted_details)

    # Update conversation state
    for field in TravelSearchExtraction.model_fields:

        value = getattr(extracted_details, field)

        if value is None:
            continue

        if field == "preferences":

            search_state[field] = list(
                dict.fromkeys(
                    search_state[field] + value
                )
            )

        else:

            search_state[field] = value

        # Map extracted adult count to hotel guest count
        if (
            search_state["search_category"] == "hotel"
            and search_state["guests"] is None
            and search_state.get("adults") is not None
        ):

            search_state["guests"] = search_state["adults"]
            
    # Reject implausible or past travel dates before calling an API.
    date_fields = (
        "check_in_date",
        "check_out_date",
        "departure_date",
        "return_date",
        "journey_date",
    )

    for date_field in date_fields:
        date_value = search_state.get(date_field)
        if date_value is not None and not (
            date.today() <= date_value <= date.today().replace(
                year=date.today().year + 10
            )
        ):
            search_state[date_field] = None

    # Correct LLM date interpretation using the exact latest user message.
    apply_deterministic_dates(search_state, user_query)

    # Validate hotel dates
    if (
        search_state["search_category"] == "hotel"
        and search_state["check_in_date"]
        and search_state["check_out_date"]
        and search_state["check_out_date"]
        <= search_state["check_in_date"]
    ):

        search_state["check_out_date"] = None

        return {
            "status": "awaiting_information",
            "message": (
                "Check-out date must be after check-in date. "
                "Please provide a valid date."
            )
        }

    # Validate flight dates
    if (
        search_state["search_category"] == "flight"
        and search_state["trip_type"] == "round_trip"
        and search_state["departure_date"]
        and search_state["return_date"]
        and search_state["return_date"]
        <= search_state["departure_date"]
    ):

        search_state["return_date"] = None

        return {
            "status": "awaiting_information",
            "message": (
                "Return date must be after departure date. "
                "Please provide a valid return date."
            )
        }

    missing_information = get_missing_search_information(
        search_state
    )

    if missing_information:

        return {
            "status": "awaiting_information",
            "missing_information": missing_information,
            "message": generate_search_followup(
                missing_information
            )
        }

    return {
        "status": "ready_to_search",
        "search_request": search_state.copy()
    }


# =========================================================
# 8. STAYAPI DESTINATION LOOKUP
# =========================================================

def get_stayapi_destination(destination: str):

    destination_file = Path(
        "data/api_responses/varanasi_destination.json"
    )

    # Reuse saved Varanasi destination
    if (
        destination.lower().strip() == "varanasi"
        and destination_file.exists()
    ):

        print("\nUsing cached Varanasi destination data.")

        with open(
            destination_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    print("\nLooking up destination:", destination)

    return lookup_destination(destination)


# =========================================================
# 9. HOTEL SEARCH
# =========================================================

def search_stayapi_hotels(search_request: dict):

    print("\n========== STAYAPI HOTEL SEARCH ==========")

    destination = search_request["destination"]

    destination_data = get_stayapi_destination(
        destination
    )

    if not destination_data.get("success"):

        return {
            "status": "error",
            "message": "Unable to identify the requested destination."
        }

    dest_id = destination_data["dest_id"]
    dest_type = destination_data["dest_type"]

    checkin = search_request["check_in_date"]
    checkout = search_request["check_out_date"]

    if hasattr(checkin, "isoformat"):
        checkin = checkin.isoformat()

    if hasattr(checkout, "isoformat"):
        checkout = checkout.isoformat()

    print("Destination ID:", dest_id)
    print("Check-in:", checkin)
    print("Check-out:", checkout)
    print("Guests:", search_request["guests"])

    results = search_hotels(

        dest_id=dest_id,
        dest_type=dest_type,
        checkin=checkin,
        checkout=checkout,
        adults=search_request["guests"],
        rooms=1

    )

    if not results.get("success"):

        return {
            "status": "error",
            "message": results.get(
                "message",
                "Unable to find hotels."
            )
        }

    formatted_hotels = format_stayapi_hotels(results)

    return {

        "status": "completed",
        "search_category": "hotel",
        "destination": destination,
        "check_in_date": checkin,
        "check_out_date": checkout,
        "guests": search_request["guests"],
        "hotels": formatted_hotels

    }


# =========================================================
# 10. FORMAT HOTEL RESULTS
# =========================================================

def format_hotel_results_for_user(search_result: dict):

    hotels = search_result.get("hotels", [])

    if not hotels:
        return "No hotels were found for your search."

    destination = search_result.get("destination")
    checkin = search_result.get("check_in_date")
    checkout = search_result.get("check_out_date")
    guests = search_result.get("guests")

    message = []

    message.append(
        f"Here are the hotels I found in {destination}:"
    )

    message.append(
        f"\nStay: {checkin} to {checkout}"
    )

    message.append(
        f"Guests: {guests}"
    )

    message.append("\n========== HOTEL OPTIONS ==========")

    for index, hotel in enumerate(hotels, start=1):

        message.append(
            f"\n{index}. {hotel.get('name', 'Unknown Hotel')}"
        )

        address = hotel.get("address")

        if address:
            message.append(f"Address: {address}")

        distance = hotel.get("distance")

        if distance:
            message.append(f"Distance: {distance}")

        price = hotel.get("display_price")

        if price:
            message.append(f"Displayed price: {price}")

        rating = hotel.get("guest_rating")
        reviews = hotel.get("review_count")

        if rating is not None:

            rating_text = f"Guest rating: {rating}"

            if reviews is not None:
                rating_text += f" ({reviews} reviews)"

            message.append(rating_text)

        else:
            message.append("Guest rating: Not available")

        room = hotel.get("room_name")

        if room:
            message.append(f"Room: {room}")

        cancellation = hotel.get("free_cancellation")

        if cancellation is True:
            message.append("Free cancellation: Available")

        elif cancellation is False:
            message.append("Free cancellation: Not available")

        prepayment = hotel.get("no_prepayment")

        if prepayment is True:
            message.append("Prepayment: Not required")

        elif prepayment is False:
            message.append("Prepayment: Required")

        image_url = hotel.get("image_url")

        if image_url:
            message.append(f"Image: {image_url}")

        message.append("-" * 35)

    message.append(
        "\nNote: Prices are displayed as returned by the hotel API. "
        "Confirm the final price and conditions before booking."
    )

    return "\n".join(message)


# =========================================================
# 11. FLIGHT SEARCH
# =========================================================

def execute_flight_search(search_request: dict):

    print("\n========== FLIGHT SEARCH ==========")

    # Resolve departure airport
    origin_result = resolve_airport(
        search_request["origin"]
    )

    if not origin_result["success"]:

        return {
            "status": "error",
            "message": origin_result["message"]
        }

    # Resolve destination airport
    destination_result = resolve_airport(
        search_request["destination"]
    )

    if not destination_result["success"]:

        return {
            "status": "error",
            "message": destination_result["message"]
        }

    departure_date = search_request[
        "departure_date"
    ].isoformat()

    return_date = search_request.get("return_date")

    if return_date:
        return_date = return_date.isoformat()

    # Call SerpApi
    results = search_flights(

        departure_id=origin_result["airport_code"],
        arrival_id=destination_result["airport_code"],
        outbound_date=departure_date,
        return_date=return_date,
        adults=search_request.get("adults") or 1,
        travel_class=search_request.get("travel_class") or 1

    )

    return {

    "status": "completed",
    "search_category": "flight",
    "origin": origin_result,
    "destination": destination_result,
    "departure_date": departure_date,
    "return_date": return_date,

    "flights": (
        results.get("best_flights", [])
        + results.get("other_flights", [])
    )[:10],

    "formatted_message": format_flight_results(results)

    }


# =========================================================
# 12. TRAIN STATION SELECTION
# =========================================================

def match_station_selection(user_query: str, candidates: list):

    query = user_query.strip().lower()

    # Match station code, name or display name
    for station in candidates:

        possible_values = [

            station.get("station_code", ""),
            station.get("station_name", ""),
            station.get("display_name", "")

        ]

        for value in possible_values:

            if value and query == value.strip().lower():
                return station

    # Match numeric selection: 1, 2, 3...
    if query.isdigit():

        index = int(query) - 1

        if 0 <= index < len(candidates):
            return candidates[index]

    return None


def create_station_selection_message(
    location: str,
    stations: list
):

    message = [
        f"Multiple railway stations were found for {location}.",
        "Please select your preferred station:"
    ]

    for index, station in enumerate(stations, start=1):

        message.append(
            f"{index}. "
            f"{station.get('display_name') or station.get('station_name')} "
            f"({station.get('station_code')})"
        )

    message.append(
        "\nReply with the number or station code."
    )

    return "\n".join(message)


def resolve_train_endpoint(
    search_state: dict,
    endpoint: str
):
    """
    Resolve origin or destination to a railway station code.

    If multiple stations are found, ask the user to choose.
    """

    if endpoint == "origin":

        location = search_state["origin"]
        code_field = "origin_station_code"
        name_field = "origin_station_name"

    else:

        location = search_state["destination"]
        code_field = "destination_station_code"
        name_field = "destination_station_name"

    # Already resolved
    if search_state.get(code_field):

        return {
            "status": "resolved"
        }

    print("\nResolving railway station:", location)

    station_result = resolve_train_station(location)

    stations = station_result.get("stations", [])

    if not stations:

        return {
            "status": "error",
            "message": (
                f"No railway stations were found for {location}. "
                "Please provide another station name or city."
            )
        }

    # Only one station found
    if len(stations) == 1:

        selected = stations[0]

        search_state[code_field] = selected["station_code"]

        search_state[name_field] = (
            selected.get("display_name")
            or selected.get("station_name")
        )

        return {
            "status": "resolved"
        }

    # Multiple stations found
    search_state["_pending_station_field"] = endpoint

    search_state["_pending_station_candidates"] = stations

    return {

        "status": "awaiting_station_selection",

        "message": create_station_selection_message(
            location,
            stations
        )

    }


def process_station_selection(
    user_query: str,
    conversation_id: str
):

    search_state = travel_search_states.get(
        conversation_id
    )

    if not search_state:
        return None

    pending_field = search_state.get(
        "_pending_station_field"
    )

    if not pending_field:
        return None

    candidates = search_state.get(
        "_pending_station_candidates",
        []
    )

    selected_station = match_station_selection(
        user_query,
        candidates
    )

    if selected_station is None:

        return {

            "status": "awaiting_station_selection",

            "message": (
                "I couldn't identify your selection. "
                "Please reply with a valid station number or code."
            )

        }

    # Save selected station
    if pending_field == "origin":

        search_state["origin_station_code"] = (
            selected_station["station_code"]
        )

        search_state["origin_station_name"] = (
            selected_station.get("display_name")
            or selected_station.get("station_name")
        )

    else:

        search_state["destination_station_code"] = (
            selected_station["station_code"]
        )

        search_state["destination_station_name"] = (
            selected_station.get("display_name")
            or selected_station.get("station_name")
        )

    search_state["_pending_station_field"] = None
    search_state["_pending_station_candidates"] = []

    print("\nSelected railway station:", selected_station)

    return None


# =========================================================
# 13. TRAIN SEARCH
# =========================================================

def execute_train_search(search_request: dict):

    print("\n========== RAILCORE TRAIN SEARCH ==========")

    # Resolve origin station
    origin_result = resolve_train_endpoint(
        search_request,
        "origin"
    )

    if origin_result["status"] != "resolved":
        return origin_result

    # Resolve destination station
    destination_result = resolve_train_endpoint(
        search_request,
        "destination"
    )

    if destination_result["status"] != "resolved":
        return destination_result

    journey_date = search_request[
        "journey_date"
    ].isoformat()

    origin_code = search_request["origin_station_code"]
    destination_code = search_request["destination_station_code"]

    print("Origin station:", origin_code)
    print("Destination station:", destination_code)
    print("Journey date:", journey_date)

    # Call RailCore
    results = search_trains(

        from_station=origin_code,
        to_station=destination_code,
        journey_date=journey_date,
        match="station"

    )

    return {

    "status": "completed",
    "search_category": "train",

    "origin": {
        "station_name": search_request["origin_station_name"],
        "station_code": origin_code
    },

    "destination": {
        "station_name": search_request["destination_station_name"],
        "station_code": destination_code
    },

    "journey_date": journey_date,

    "trains": (
        results.get("data", results).get("trains", [])
    )[:10],

    "formatted_message": format_train_results(results)

    }


# =========================================================
# 14. MAIN TRAVEL SEARCH EXECUTION
# =========================================================

async def run_travel_search(
    user_query: str,
    conversation_id: str = "default"
):

    print("\n========== TRAVEL SEARCH STARTED ==========")

    # Step 1: Check for a pending station selection
    existing_state = travel_search_states.get(
        conversation_id
    )

    if (
        existing_state
        and existing_state.get("_pending_station_field")
    ):

        selection_result = process_station_selection(
            user_query,
            conversation_id
        )

        if selection_result:
            return selection_result

        # Reuse existing train search details
        collection_result = {
            "status": "ready_to_search",
            "search_request": existing_state
        }

    else:

        # Step 2: Collect search details
        collection_result = collect_travel_search_details(

            user_query=user_query,
            conversation_id=conversation_id

        )

    # Step 3: Check missing information
    if collection_result["status"] == "awaiting_information":

        return collection_result

    search_request = collection_result["search_request"]

    category = search_request["search_category"]

    if category == "train":
        search_request = travel_search_states[conversation_id]

    category = search_request["search_category"]

    # Step 4: Route to correct service

    try:

        # HOTEL SEARCH
        if category == "hotel":

            search_result = search_stayapi_hotels(
                search_request
            )

            if search_result.get("status") == "completed":

                search_result["formatted_message"] = (
                    format_hotel_results_for_user(search_result)
                )

        # FLIGHT SEARCH
        elif category == "flight":

            search_result = execute_flight_search(
                search_request
            )

        # TRAIN SEARCH
        elif category == "train":

            search_result = execute_train_search(
                search_request
            )

        else:

            return {
                "status": "error",
                "message": "Unsupported travel search category."
            }

    except Exception as error:

        print("\nTravel Search API Error:", str(error))

        return {

            "status": "error",

            "message": (
                "Something went wrong while searching. "
                "Please try again later."
            )

        }

    # Step 5: Preserve state if station selection is pending
    if search_result.get("status") == "awaiting_station_selection":

        return search_result

    # Step 6: Preserve completed search results
    if search_result.get("status") == "completed":

        travel_search_results[conversation_id] = search_result

        print(
            "\nSaved search results:",
            search_result.get("search_category")
        )

        # Clear temporary search collection state
        travel_search_states.pop(
            conversation_id,
            None
        )

    return search_result
