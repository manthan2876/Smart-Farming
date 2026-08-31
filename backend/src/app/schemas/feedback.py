from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class FeedbackRequest(BaseModel):
    prediction_id: int = Field(gt=0)
    is_correct: bool
    farmer_note: str | None = Field(default=None, max_length=2000)

class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    is_correct: bool
    farmer_note: str | None