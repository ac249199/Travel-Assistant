
from app.agents.travel_search import (
    collect_travel_search_details,
    travel_search_states
)


conversation_id = "hotel_search_test_1"


# Turn 1
print("\n========== TURN 1 ==========")

result = collect_travel_search_details(
    "Find hotels in Varanasi.",
    conversation_id
)

print(result)


# Turn 2
print("\n========== TURN 2 ==========")

result = collect_travel_search_details(
    "Check-in 25 November 2026 and check-out 28 November 2026.",
    conversation_id
)

print(result)


# Turn 3
print("\n========== TURN 3 ==========")

result = collect_travel_search_details(
    "2 guests.",
    conversation_id
)

print(result)


# Final state
print("\n========== FINAL SEARCH STATE ==========")
print(travel_search_states[conversation_id])
