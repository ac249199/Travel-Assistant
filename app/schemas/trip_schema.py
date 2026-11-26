from pydantic import BaseModel, Field


class TripPlanningRequest(BaseModel):

    destination: str = Field(
        description="City or destination where the user wants to travel"
    )

    duration_days: int = Field(
        gt=0,
        description="Total number of days for the trip"
    )

    travellers: int = Field(
        gt=0,
        description="Total number of people travelling"
    )