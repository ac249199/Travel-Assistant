from app.schemas.trip_schema import TripPlanningRequest


# Test 1: Valid input
trip = TripPlanningRequest(
    destination="Goa",
    duration_days=4,
    travellers=2
)

print("Test 1: Valid input")
print(trip)
print()


# Test 2: Invalid duration
try:
    trip = TripPlanningRequest(
        destination="Goa",
        duration_days=0,
        travellers=2
    )
except Exception as e:
    print("Test 2: Invalid duration")
    print(e)
    print()


# Test 3: Invalid travellers
try:
    trip = TripPlanningRequest(
        destination="Goa",
        duration_days=4,
        travellers=0
    )
except Exception as e:
    print("Test 3: Invalid travellers")
    print(e)