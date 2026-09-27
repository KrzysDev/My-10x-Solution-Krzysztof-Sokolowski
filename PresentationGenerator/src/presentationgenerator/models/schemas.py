"""
Pydantic models and schemas for PresentationGenerator.
"""

from typing import Union
from pydantic import BaseModel, ConfigDict, Field


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
