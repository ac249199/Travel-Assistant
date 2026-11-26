
from app.agents.trip_planner import generate_trip_plan
from app.schemas.trip_schema import TripPlanningRequest


# Create a sample trip request
request = TripPlanningRequest(
    destination="Jaipur",
    duration_days=3,
    travellers=2
)
# Generate itinerary
result = generate_trip_plan(request)

# Display result
print("\n========== GENERATED TRIP PLAN ==========\n")
print(result)
