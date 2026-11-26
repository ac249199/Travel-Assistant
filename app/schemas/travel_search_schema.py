
from pydantic import BaseModel, Field, model_validator
from typing import Literal
from datetime import date


class TravelSearchRequest(BaseModel):

    search_category: Literal[
        "hotel",
        "restaurant",
        "transport",
        "activity"
    ] = Field(
        description="Type of travel service the user wants to search for"
    )

    destination: str = Field(
        description="City or destination for the search"
    )

    check_in_date: date = Field(
        description="Start date of the search or stay"
    )

    check_out_date: date = Field(
        description="End date of the search or stay"
    )

    guests: int = Field(
        gt=0,
        description="Number of people travelling"
    )

    budget_per_night: float | None = Field(
        default=None,
        gt=0,
        description="Maximum budget per night, if applicable"
    )

    preferences: list[str] = Field(
        default_factory=list,
        description="User preferences such as budget-friendly, luxury, or swimming pool"
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError(
                "Check-out date must be after check-in date"
            )
        return self
