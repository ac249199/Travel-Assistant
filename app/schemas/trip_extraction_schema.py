
from pydantic import BaseModel, Field


class TripDetailsExtraction(BaseModel):

    destination: str | None = Field(
        default=None,
        description="Destination provided by the user"
    )

    duration_days: int | None = Field(
        default=None,
        gt=0,
        description="Number of trip days provided by the user"
    )

    travellers: int | None = Field(
        default=None,
        gt=0,
        description="Number of travellers provided by the user"
    )
