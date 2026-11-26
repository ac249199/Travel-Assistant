
from app.services import train_service


# Mock RailCore response
mock_response = {
    "success": True,
    "data": {
        "results": [
            {
                "station_code": "BSB",
                "station_name": "Varanasi Junction",
                "display_name": "Varanasi Junction (BSB)",
                "city": "Varanasi",
                "state": "Uttar Pradesh",
                "confidence": 0.99
            },
            {
                "station_code": "BSBS",
                "station_name": "Banaras",
                "display_name": "Banaras (BSBS)",
                "city": "Varanasi",
                "state": "Uttar Pradesh",
                "confidence": 0.95
            }
        ]
    }
}


# Replace the real API function with mock data
train_service.search_stations = lambda query, limit=5: mock_response


result = train_service.resolve_train_station("Varanasi")

print("Station search results:")

for station in result["stations"]:
    print(
        f'{station["display_name"]} | '
        f'Code: {station["station_code"]} | '
        f'Confidence: {station["confidence"]}'
    )


# Test cache
second_result = train_service.resolve_train_station("Varanasi")

print("\nCache test:", result is second_result)
