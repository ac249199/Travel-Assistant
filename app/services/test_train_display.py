
from app.services.train_service import format_train_results


mock_data = {
    "success": True,
    "data": {
        "from_station_code": "BSL",
        "to_station_code": "ADI",
        "journey_date": "2026-11-28",
        "quota": "GN",
        "matched_by": "station",
        "trains": [
            {
                "train_number": "12656",
                "from_station_code": "BSL",
                "from_station_name": "Bhusaval Junction",
                "to_station_code": "ADI",
                "to_station_name": "Ahmedabad Junction",
                "train_name": "NAVJEEVAN SF EXP",
                "extended_train_name": "Navjeevan SF Express",
                "departure_time": "10:25",
                "arrival_time": "18:00",
                "duration_minutes": 455,
                "distance_km": 563,
                "train_type": "SF",
                "classes": ["SL", "3A", "2A", "1A"],
                "running_days": [
                    "MON", "TUE", "WED", "THU",
                    "FRI", "SAT", "SUN"
                ],
                "has_pantry": True,
                "availability_summary": [
                    {
                        "class_code": "3A",
                        "status": "AVAILABLE",
                        "text": "AVAILABLE-4",
                        "fare": 965,
                        "confidence": "high"
                    }
                ]
            }
        ]
    }
}

print(format_train_results(mock_data))
