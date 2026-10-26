from __future__ import annotations
from pydantic import BaseModel

class CropListResponse(BaseModel):
    crops: list[str]