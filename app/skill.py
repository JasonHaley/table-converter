"""Types for AI Search custom skills interface: https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-interface."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

__all__ = (
    "AISearchSkillInput",
    "AISearchSkillInputRecord",
    "AISearchSkillIssue",
    "AISearchSkillOutput",
    "AISearchSkillOutputRecord",
)

InputData = TypeVar("InputData", bound=BaseModel)
OutputData = TypeVar("OutputData", bound=BaseModel)


class AISearchSkillIssue(BaseModel):
    """A warning or error message from the skill."""

    message: str


class AISearchSkillInputRecord(BaseModel, Generic[InputData]):
    """Individual skill input item."""

    record_id: str = Field(validation_alias="recordId")
    data: InputData


InputRecord = TypeVar("InputRecord", bound=AISearchSkillInputRecord)


class AISearchSkillInput(BaseModel, Generic[InputRecord]):
    """Skill input data."""

    values: tuple[InputRecord, ...]


class AISearchSkillOutputRecord(BaseModel, Generic[OutputData]):
    """Individual skill output item."""

    record_id: str = Field(serialization_alias="recordId")
    data: OutputData
    errors: tuple[AISearchSkillIssue, ...] = Field(default_factory=tuple)
    warnings: tuple[AISearchSkillIssue, ...] = Field(default_factory=tuple)


OutputRecord = TypeVar("OutputRecord", bound=AISearchSkillOutputRecord)


class AISearchSkillOutput(BaseModel, Generic[OutputRecord]):
    """Skill output data."""

    values: tuple[OutputRecord, ...]
