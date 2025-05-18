"""Types for AI Search custom skills interface: https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-interface."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field

__all__ = (
    "AISearchSkillInput",
    "AISearchSkillInputRecord",
    "AISearchSkillIssue",
    "AISearchSkillOutput",
    "AISearchSkillOutputRecord",
)

class AISearchSkillIssue(BaseModel):
    """A warning or error message from the skill."""

    message: str


class TableConverterInput(BaseModel):
    """Input data for the table converter model."""

    text: str | None

class AISearchSkillInputRecord(BaseModel):
    """Skill input item."""

    record_id: str = Field(validation_alias="recordId")
    data: TableConverterInput = Field(default_factory=lambda: TableConverterInput(text=None))

class TableConverterInputRecord(AISearchSkillInputRecord):
    """Individual input record for the table converter model."""

class AISearchSkillInput(BaseModel):
    """Skill input data."""

    values: List[AISearchSkillInputRecord] = []


class TableConverterOutput(BaseModel):
    """Output data from the table converter model."""

    text: str | None

class AISearchSkillOutputRecord(BaseModel):
    """Skill output item."""

    record_id: str = Field(serialization_alias="recordId")
    data: TableConverterOutput = Field(default_factory=lambda: TableConverterOutput(text=None))
    errors: List[AISearchSkillIssue] = Field(default_factory=list)
    warnings: List[AISearchSkillIssue] = Field(default_factory=list)

class TableConverterOutputRecord(AISearchSkillOutputRecord):
    """Individual output record from the table converter model."""

class AISearchSkillOutput(BaseModel):
    """Skill output data."""

    values: List[AISearchSkillOutputRecord] = []

class TableConverterSkillOutput(AISearchSkillOutput):
    """Output for the table converter skill."""
