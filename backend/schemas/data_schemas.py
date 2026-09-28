from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import date

class CSVImportResponse(BaseModel):
    success: bool
    records_inserted: int
    errors: Optional[List[str]] = None
    message: str

class DBStatsResponse(BaseModel):
    total_users: int
    total_farmers: int
    total_policies: int
    total_claims: int
    total_weather_records: int
    total_enso_records: int
    total_survival_records: int

class DatasetQualityResponse(BaseModel):
    missing_values: Dict[str, int]
    censorship_rate: float
    total_records: int
    el_nino_events: int
    la_nina_events: int
    neutral_events: int

class DataFilterRequest(BaseModel):
    region: Optional[str] = None
    crop_type: Optional[str] = None
    enso_phase: Optional[str] = None
