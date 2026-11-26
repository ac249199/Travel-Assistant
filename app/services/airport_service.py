
# Common Indian airport mappings

AIRPORT_CODES = {
    "varanasi": {
        "code": "VNS",
        "name": "Lal Bahadur Shastri International Airport"
    },
    "delhi": {
        "code": "DEL",
        "name": "Indira Gandhi International Airport"
    },
    "new delhi": {
        "code": "DEL",
        "name": "Indira Gandhi International Airport"
    },
    "mumbai": {
        "code": "BOM",
        "name": "Chhatrapati Shivaji Maharaj International Airport"
    },
    "bangalore": {
        "code": "BLR",
        "name": "Kempegowda International Airport"
    },
    "bengaluru": {
        "code": "BLR",
        "name": "Kempegowda International Airport"
    },
    "kolkata": {
        "code": "CCU",
        "name": "Netaji Subhas Chandra Bose International Airport"
    },
    "chennai": {
        "code": "MAA",
        "name": "Chennai International Airport"
    },
    "hyderabad": {
        "code": "HYD",
        "name": "Rajiv Gandhi International Airport"
    },
    "lucknow": {
        "code": "LKO",
        "name": "Chaudhary Charan Singh International Airport"
    },
    "pune": {
        "code": "PNQ",
        "name": "Pune Airport"
    },
    "jaipur": {
        "code": "JAI",
        "name": "Jaipur International Airport"
    },
    "goa": {
        "code": "GOI",
        "name": "Goa Dabolim Airport"
    },
    "ahmedabad": {
        "code": "AMD",
        "name": "Sardar Vallabhbhai Patel International Airport"
    }
}


def resolve_airport(city: str):

    normalized_city = city.strip().lower()

    airport = AIRPORT_CODES.get(normalized_city)

    if not airport:
        return {
            "success": False,
            "message": f"Airport mapping not available for {city}."
        }

    return {
        "success": True,
        "city": city,
        "airport_code": airport["code"],
        "airport_name": airport["name"]
    }
