
from pydantic import BaseModel, Field, EmailStr
from typing import Literal


class BookingRequest(BaseModel):

    service_type: Literal[
        "hotel",
        "flight",
        "train"
    ] = Field(
        description="Type of travel service selected by the user"
    )

    service_name: str = Field(
        description="Name of the selected hotel, flight or train"
    )

    customer_name: str = Field(
        description="Full name of the customer"
    )

    customer_email: EmailStr = Field(
        description="Valid email address of the customer"
    )
