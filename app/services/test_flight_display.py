
from app.services.flight_service import format_flight_results


mock_data = {
    "search_parameters": {
        "currency": "INR"
    },
    "best_flights": [
        {
            "flights": [
                {
                    "airline": "IndiGo",
                    "flight_number": "6E 201",
                    "departure_airport": {
                        "name": "Varanasi Airport",
                        "id": "VNS",
                        "time": "2026-12-10 08:00"
                    },
                    "arrival_airport": {
                        "name": "Delhi Airport",
                        "id": "DEL",
                        "time": "2026-12-10 09:35"
                    }
                }
            ],
            "total_duration": 95,
            "price": 4500
        }
    ],
    "other_flights": []
}


result = format_flight_results(mock_data)

print(result)
