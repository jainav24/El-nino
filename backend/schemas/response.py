from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class RiskFactor(BaseModel):
    feature: str
    readable_name: str
    contribution: float
    direction: str
    hazard_ratio: Optional[float]

class PredictionResponse(BaseModel):
    success: bool
    overall_risk_score: Optional[float] = None
    risk_category: Optional[str] = None
    estimated_time_to_claim: Optional[str] = None
    estimated_time_to_claim_days: Optional[float] = None
    survival_probability: Optional[Dict[str, float]] = None
    claim_probability: Optional[Dict[str, float]] = None
    explanation: Optional[str] = None
    top_contributing_factors: Optional[List[RiskFactor]] = None
    preliminary_weather_risk_score: Optional[int] = None
    model_version: Optional[str] = None
    errors: Optional[List[str]] = None

class ScenarioSummary(BaseModel):
    risk_score: float
    risk_category: str
    claim_probability_180d: Optional[float]
    explanation: str

class ChangedInput(BaseModel):
    from_: Any
    to: Any
    
    model_config = {
        "populate_by_name": True,
        "alias_generator": lambda string: "from" if string == "from_" else string
    }

class WhatIfResponse(BaseModel):
    success: bool
    current_scenario: Optional[ScenarioSummary] = None
    alternative_scenario: Optional[ScenarioSummary] = None
    delta_risk_score: Optional[float] = None
    delta_direction: Optional[str] = None
    changed_inputs: Optional[Dict[str, ChangedInput]] = None
    what_if_summary: Optional[str] = None
    errors: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str

class ModelInfoResponse(BaseModel):
    version: str
    description: str
    baseline_concordance: float
    proposed_concordance: float
    feature_count: int

class StatisticsResponse(BaseModel):
    total_predictions: int
    average_risk_score: float
    risk_category_distribution: Dict[str, int]

class HistoryItem(BaseModel):
    id: int
    timestamp: datetime
    state: str
    crop_type: str
    risk_score: float
    risk_category: str
    explanation: str

class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
