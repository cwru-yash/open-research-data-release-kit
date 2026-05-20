from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CanonicalRecord(BaseModel):
    source: str
    domain: str
    dataset_id: str
    record_id: str
    observed_at: datetime
    variable: str
    value: float | None
    unit: str | None = None
    quality_flag: str | None = None
    location_or_instrument: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
