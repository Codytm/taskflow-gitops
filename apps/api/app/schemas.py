from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def strip_title(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        raise ValueError("title cannot be blank")
    return stripped


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    notes: str = ""

    @field_validator("title")
    @classmethod
    def title_is_not_blank(cls, value: str) -> str:
        return strip_title(value)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    notes: str | None = None
    done: bool | None = None

    @field_validator("title")
    @classmethod
    def title_is_not_blank(cls, value: str | None) -> str | None:
        return strip_title(value)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    notes: str
    done: bool
    created_at: datetime
