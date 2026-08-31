from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class CropListResponse(BaseModel):
    crops: list[str]