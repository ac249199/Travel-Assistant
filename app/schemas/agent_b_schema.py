from pydantic import BaseModel, Field
from typing import Literal


class AgentBWorkflow(BaseModel):

    workflow: Literal[
        "trip_planning",
        "travel_search",
        "booking"
    ] = Field(
        description="The workflow that Agent B should execute"
    )

    reason: str = Field(
        description="A short explanation for selecting this workflow"
    )