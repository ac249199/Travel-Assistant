
from pydantic import BaseModel, Field
from typing import Literal


class IntentClassification(BaseModel):

    intent: Literal[
        "travel_information",
        "trip_planning",
        "travel_search",
        "booking",
        "general"
    ] = Field(
        description="The primary intention of the user's query"
    )

    target_agent: Literal[
        "agent_a",
        "agent_b",
        "general"
    ] = Field(
        description="The agent responsible for handling the query"
    )

    reason: str = Field(
        description="A short explanation for the classification"
    )

    clarification_needed: bool = Field(
        description="Whether additional user information is required"
    )

    missing_information: list[str] = Field(
        description="List of essential missing details, if any"
    )
