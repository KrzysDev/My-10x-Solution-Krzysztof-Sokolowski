"""
Pydantic models and schemas for PresentationGenerator.
"""

from typing import Union
from pydantic import BaseModel, ConfigDict, Field
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr

class TextChunk(BaseModel):
    """
    Represents a chunk of text extracted from a document.
    """
    id: int
    content: Union[list[str], str]

    @property
    def text(self) -> str:
        """
        Returns chunk content as a joined string.
        """
        if isinstance(self.content, list):
            return " ".join(self.content)
        return self.content


class Plan(BaseModel):
    """
    Represents a generated slide plan as plain bullet points text.
    """
    model_config = ConfigDict(populate_by_name=True)

    content: str = Field(alias="Content", default="")

    @property
    def Content(self) -> str:
        return self.content


class PresentationResult(BaseModel):
    """
    Represents the final generated presentation.
    """
    html: str
    slides_count: int
    topic: str
    slides: list[str] = Field(default_factory=list)

class PDFPresentationRequest(BaseModel):
    """
    Represents the request with pdf bytes
    """

    pdf: UploadFile


class EmailPasswordRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRequest(BaseModel):
    token: str


class SavePresentationRequest(BaseModel):
    """Request body for manually saving a generated presentation."""
    token: str
    topic: str
    html: str
    slides_count: int


class SavedPresentation(BaseModel):
    """A presentation row returned from the database (list view — no HTML)."""
    id: str
    user_id: str
    topic: str
    slides_count: int
    created_at: str


class SavedPresentationFull(BaseModel):
    """A single presentation row with full HTML (detail view)."""
    id: str
    user_id: str
    topic: str
    slides_count: int
    html: str
    created_at: str
