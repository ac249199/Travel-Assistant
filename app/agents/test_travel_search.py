
from app.agents.travel_search import (
    get_missing_search_information,
    generate_search_followup
)


# Test 1: Hotel search with missing details
hotel_state = {
    "search_category": "hotel",
    "destination": "Varanasi",
    "origin": None,
    "check_in_date": None,
    "check_out_date": None,
    "guests": None,
    "budget_per_night": None,
    "preferences": []
}

missing = get_missing_search_information(hotel_state)

print("\nTEST 1: HOTEL SEARCH")
print("Missing Information:", missing)
print(generate_search_followup(missing))


# Test 2: Restaurant search
restaurant_state = {
    "search_category": "restaurant",
    "destination": "Varanasi",
    "origin": None,
    "check_in_date": None,
    "check_out_date": None,
    "guests": None,
    "budget_per_night": None,
    "preferences": []
}

missing = get_missing_search_information(restaurant_state)

print("\nTEST 2: RESTAURANT SEARCH")
print("Missing Information:", missing)


# Test 3: Transport search
transport_state = {
    "search_category": "transport",
    "destination": "Varanasi Airport",
    "origin": None,
    "check_in_date": None,
    "check_out_date": None,
    "guests": None,
    "budget_per_night": None,
    "preferences": []
}

missing = get_missing_search_information(transport_state)

print("\nTEST 3: TRANSPORT SEARCH")
print("Missing Information:", missing)


# Test 4: Activity search
activity_state = {
    "search_category": "activity",
    "destination": "Varanasi",
    "origin": None,
    "check_in_date": None,
    "check_out_date": None,
    "guests": None,
    "budget_per_night": None,
    "preferences": []
}

missing = get_missing_search_information(activity_state)

print("\nTEST 4: ACTIVITY SEARCH")
print("Missing Information:", missing)
