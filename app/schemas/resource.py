"""Pydantic schémata pro validaci Resource Card vstupů a výstupů API."""

from datetime import date

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.schemas.enums import (
    ACCESS_CONDITIONS_VALUES,
    AUDIENCE_VALUES,
    EFFORT_LEVEL_VALUES,
    PERSONA_VALUES,
    PRACTICALITY_LEVEL_VALUES,
    RESOURCE_TYPE_VALUES,
    REVIEW_STATUS_VALUES,
    STAGE_VALUES,
    TASK_VALUES,
)


class ResourceCardBase(BaseModel):
    resource_id: str
    title: str
    url: HttpUrl
    short_description: str
    resource_type: str
    audience: list[str]
    mapped_tasks: list[str]
    mapped_stages: list[str]
    mapped_personas: list[str]
    effort_level: str
    practicality_level: str
    language: str
    keywords_tags: list[str]
    topic_area: str
    recommended_rank: int | None = None
    featured_m6: bool
    quality_note: str
    source_owner_org: str
    source_year_or_last_update: str
    access_conditions: str
    contributor_partner: str
    review_status: str
    review_due_date: date
    last_checked_date: date
    editor_notes: str = ""

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, v: str) -> str:
        if v not in RESOURCE_TYPE_VALUES:
            raise ValueError(f"resource_type must be one of {sorted(RESOURCE_TYPE_VALUES)}")
        return v

    @field_validator("effort_level")
    @classmethod
    def validate_effort_level(cls, v: str) -> str:
        if v not in EFFORT_LEVEL_VALUES:
            raise ValueError(f"effort_level must be one of {sorted(EFFORT_LEVEL_VALUES)}")
        return v

    @field_validator("practicality_level")
    @classmethod
    def validate_practicality_level(cls, v: str) -> str:
        if v not in PRACTICALITY_LEVEL_VALUES:
            raise ValueError(f"practicality_level must be one of {sorted(PRACTICALITY_LEVEL_VALUES)}")
        return v

    @field_validator("access_conditions")
    @classmethod
    def validate_access_conditions(cls, v: str) -> str:
        if v not in ACCESS_CONDITIONS_VALUES:
            raise ValueError(f"access_conditions must be one of {sorted(ACCESS_CONDITIONS_VALUES)}")
        return v

    @field_validator("review_status")
    @classmethod
    def validate_review_status(cls, v: str) -> str:
        if v not in REVIEW_STATUS_VALUES:
            raise ValueError(f"review_status must be one of {sorted(REVIEW_STATUS_VALUES)}")
        return v

    @field_validator("audience")
    @classmethod
    def validate_audience(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - AUDIENCE_VALUES)
        if unknown:
            raise ValueError(f"audience contains unknown values: {unknown}")
        return values

    @field_validator("mapped_tasks")
    @classmethod
    def validate_mapped_tasks(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - TASK_VALUES)
        if unknown:
            raise ValueError(f"mapped_tasks contains unknown values: {unknown}")
        return values

    @field_validator("mapped_stages")
    @classmethod
    def validate_mapped_stages(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - STAGE_VALUES)
        if unknown:
            raise ValueError(f"mapped_stages contains unknown values: {unknown}")
        return values

    @field_validator("mapped_personas")
    @classmethod
    def validate_mapped_personas(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - PERSONA_VALUES)
        if unknown:
            raise ValueError(f"mapped_personas contains unknown values: {unknown}")
        return values


class ResourceCardCreate(ResourceCardBase):
    pass


class ResourceCardUpdate(ResourceCardBase):
    pass


class ResourceCardOut(ResourceCardBase):
    model_config = {"from_attributes": True}


class ResourceCardSummary(BaseModel):
    resource_id: str
    title: str
    url: HttpUrl
    short_description: str


class EnrichRequest(BaseModel):
    title: str | None = None
    url: HttpUrl


class EnrichResponse(BaseModel):
    title: str | None = None
    short_description: str | None = None
    resource_type: str | None = None
    effort_level: str | None = None
    practicality_level: str | None = None
    topic_area: str | None = None
    source_owner_org: str | None = None
    source_year_or_last_update: str | None = None
    access_conditions: str | None = None
    contributor_partner: str | None = None
    quality_note: str | None = None
    editor_notes: str | None = None
    language: str | None = None
    keywords_tags: list[str] = Field(default_factory=list)
    mapped_tasks: list[str] = Field(default_factory=list)
    mapped_stages: list[str] = Field(default_factory=list)
    mapped_personas: list[str] = Field(default_factory=list)
    audience: list[str] = Field(default_factory=list)


class ResourceCardDraftCreate(BaseModel):
    resource_id: str
    title: str
    url: HttpUrl
    language: str = "EN"


class ResourceEnrichCommand(BaseModel):
    url: HttpUrl | None = None
