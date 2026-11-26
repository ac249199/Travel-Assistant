
from app.schemas.travel_search_schema import TravelSearchRequest

# Test 1: Budget provided
request1 = TravelSearchRequest(
    search_category="hotel",
    destination="Jaipur",
    check_in_date="2026-12-15",
    check_out_date="2026-12-18",
    guests=2,
    budget_per_night=2500
)

print("Test 1:", request1)

# Test 2: Budget not provided
request2 = TravelSearchRequest(
    search_category="hotel",
    destination="Goa",
    check_in_date="2026-12-20",
    check_out_date="2026-12-23",
    guests=2
)

print("\nTest 2:", request2)

# Test 3: Invalid budget
try:
    request3 = TravelSearchRequest(
        search_category="hotel",
        destination="Jaipur",
        check_in_date="2026-12-15",
        check_out_date="2026-12-18",
        guests=2,
        budget_per_night=0
    )
except Exception as e:
    print("\nTest 3: Validation Error")
    print(e)
# Test 4: Invalid same dates
try:
    TravelSearchRequest(
        search_category="hotel",
        destination="Jaipur",
        check_in_date="2026-12-15",
        check_out_date="2026-12-15",
        guests=2
    )
except Exception as e:
    print("\nTest 4: Validation Error")
    print(e)


# Test 5: Check-out before check-in
try:
    TravelSearchRequest(
        search_category="hotel",
        destination="Jaipur",
        check_in_date="2026-12-18",
        check_out_date="2026-12-15",
        guests=2
    )
except Exception as e:
    print("\nTest 5: Validation Error")
    print(e)