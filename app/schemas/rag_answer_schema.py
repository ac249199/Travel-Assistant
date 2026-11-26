
from pydantic import BaseModel, Field


class RAGAnswer(BaseModel):

    answer: str = Field(
        description="The final natural and user-friendly answer to the user's question."
    )

    source_ids: list[str] = Field(
        description="List of source IDs that were actually used to support the answer."
    )
