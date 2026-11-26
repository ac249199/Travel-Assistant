
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class TravelSearchExtraction(BaseModel):

    # Search category
    search_category: Literal[
        "hotel",
        "flight",
        "train"
    ] | None = Field(
        default=None,
        description="Type of travel search requested: hotel, flight or train"
    )

    # Common locations
    destination: str | None = Field(
        default=None,
        description="Destination city, airport or railway station"
    )

    origin: str | None = Field(
        default=None,
        description="Starting city, airport or railway station"
    )

    # Hotel fields
    check_in_date: date | None = Field(
        default=None,
        description="Hotel check-in date"
    )

    check_out_date: date | None = Field(
        default=None,
        description="Hotel check-out date"
    )

    guests: int | None = Field(
        default=None,
        gt=0,
        description="Number of hotel guests"
    )

    budget_per_night: float | None = Field(
        default=None,
        gt=0,
        description="Maximum hotel budget per night"
    )

    # Flight fields
    departure_date: date | None = Field(
        default=None,
        description="Flight departure date"
    )

    return_date: date | None = Field(
        default=None,
        description="Flight return date, if round trip"
    )

    trip_type: Literal[
        "one_way",
        "round_trip"
    ] | None = Field(
        default=None,
        description="Flight journey type"
    )

    adults: int | None = Field(
        default=None,
        ge=1,
        description="Number of adult flight passengers"
    )

    children: int = Field(
        default=0,
        ge=0,
        description="Number of child flight passengers"
    )

    infants: int = Field(
        default=0,
        ge=0,
        description="Number of infant flight passengers"
    )

    travel_class: Literal[1, 2, 3, 4] | None = Field(
        default=None,
        description="Flight class: 1 Economy, 2 Premium Economy, 3 Business, 4 First Class"
    )

    # Train fields
    journey_date: date | None = Field(
        default=None,
        description="Train journey date"
    )

    train_class: str | None = Field(
        default=None,
        description="Preferred train class such as SL, 3A, 2A or 1A"
    )

    quota: str | None = Field(
        default=None,
        description="Train booking quota, if specified"
    )

    # Common preferences
    preferences: list[str] = Field(
        default_factory=list,
        description="User preferences such as budget-friendly, luxury or preferred travel options"
    )
