"""Types for AI Search custom skills interface: https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-interface."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

__all__ = (
    "SkillInput",
    "SkillInputRecord",
    "SkillIssue",
    "SkillOutput",
    "SkillOutputRecord",
)

InputData = TypeVar("InputData", bound=BaseModel)
OutputData = TypeVar("OutputData", bound=BaseModel)


class SkillIssue(BaseModel):
    """A warning or error message from the skill."""

    message: str


class SkillInputRecord(BaseModel, Generic[InputData]):
    """Individual skill input item."""

    record_id: str = Field(validation_alias="recordId")
    data: InputData


InputRecord = TypeVar("InputRecord", bound=SkillInputRecord)


class SkillInput(BaseModel, Generic[InputRecord]):
    """Skill input data."""

    values: tuple[InputRecord, ...]


class SkillOutputRecord(BaseModel, Generic[OutputData]):
    """Individual skill output item."""

    record_id: str = Field(serialization_alias="recordId")
    data: OutputData
    errors: tuple[SkillIssue, ...] = Field(default_factory=tuple)
    warnings: tuple[SkillIssue, ...] = Field(default_factory=tuple)


OutputRecord = TypeVar("OutputRecord", bound=SkillOutputRecord)


class SkillOutput(BaseModel, Generic[OutputRecord]):
    """Skill output data."""

    values: tuple[OutputRecord, ...]
