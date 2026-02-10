from pydantic import BaseModel, Field

from .. import __version__


class VersionOut(BaseModel):
    version: str

    @classmethod
    def from_metadata(cls):
        return cls(version=__version__)


class AskRequest(BaseModel):
    """Request body for asking Genie a question."""
    question: str = Field(..., min_length=1, description="Natural language question about the data")
    conversation_id: str | None = Field(None, description="For follow-up questions in the same conversation")


class AskResponse(BaseModel):
    """Response from Genie: SQL, result table, and text summary."""
    question: str
    sql: str | None = None
    columns: list[str] = Field(default_factory=list)
    data: list[list] = Field(default_factory=list)
    row_count: int = 0
    text_response: str = ""
    conversation_id: str | None = None
    error: str | None = None
