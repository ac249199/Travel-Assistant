
from app.services.airport_service import resolve_airport


for city in ["Varanasi", "Delhi", "Mumbai", "Bangalore", "Lucknow"]:

    result = resolve_airport(city)

    print(city, "=>", result)


print("\nUnknown city test:")
print(resolve_airport("Unknown City"))
