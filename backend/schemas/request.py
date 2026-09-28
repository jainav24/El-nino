from pydantic import BaseModel, Field, field_validator
from typing import Optional
from backend.ml.risk_engine import (
    VALID_STATES, VALID_CROP_TYPES, VALID_CROP_SEASONS,
    VALID_SOIL_TYPES, VALID_IRRIGATION_TYPES,
    VALID_ELNINO_STATUSES, VALID_ELNINO_INTENSITIES,
    NUMERIC_BOUNDS
)

class PredictionRequest(BaseModel):
    # Categorical
    state: str = Field(..., description="State in India")
    crop_type: str = Field(..., description="Type of crop")
    crop_season: str = Field(..., description="Crop season")
    soil_type: str = Field(..., description="Soil type")
    irrigation_type: str = Field(..., description="Irrigation type")
    elnino_status: str = Field(..., description="El Nino Status")
    elnino_intensity: str = Field(..., description="El Nino Intensity")
    
    # Numeric
    latitude: float = Field(...)
    longitude: float = Field(...)
    farm_area: float = Field(...)
    enso_index: float = Field(...)
    normal_rainfall: float = Field(...)
    rainfall: float = Field(...)
    rainfall_deviation: float = Field(...)
    temperature: float = Field(...)
    temperature_deviation: float = Field(...)
    humidity: float = Field(...)
    soil_moisture: float = Field(...)
    drought_index: float = Field(...)
    flood_index: float = Field(...)
    extreme_weather_events: int = Field(...)
    weather_anomaly_score: float = Field(...)
    historical_yield: float = Field(...)
    insurance_amount: float = Field(...)
    premium_amount: float = Field(...)
    previous_claims: int = Field(...)
    @field_validator('state')
    def validate_state(cls, v):
        if v not in VALID_STATES:
            raise ValueError(f"Must be one of {VALID_STATES}")
        return v
        
    @field_validator('crop_type')
    def validate_crop(cls, v):
        if v not in VALID_CROP_TYPES:
            raise ValueError(f"Must be one of {VALID_CROP_TYPES}")
        return v
        
    @field_validator('crop_season')
    def validate_season(cls, v):
        if v not in VALID_CROP_SEASONS:
            raise ValueError(f"Must be one of {VALID_CROP_SEASONS}")
        return v
        
    @field_validator('soil_type')
    def validate_soil(cls, v):
        if v not in VALID_SOIL_TYPES:
            raise ValueError(f"Must be one of {VALID_SOIL_TYPES}")
        return v
        
    @field_validator('irrigation_type')
    def validate_irrigation(cls, v):
        if v not in VALID_IRRIGATION_TYPES:
            raise ValueError(f"Must be one of {VALID_IRRIGATION_TYPES}")
        return v
        
    @field_validator('elnino_status')
    def validate_elnino_status(cls, v):
        if v not in VALID_ELNINO_STATUSES:
            raise ValueError(f"Must be one of {VALID_ELNINO_STATUSES}")
        return v
        
    @field_validator('elnino_intensity')
    def validate_elnino_intensity(cls, v):
        if v not in VALID_ELNINO_INTENSITIES:
            raise ValueError(f"Must be one of {VALID_ELNINO_INTENSITIES}")
        return v

class WhatIfRequest(BaseModel):
    current_scenario: PredictionRequest
    alternative_scenario: PredictionRequest

class RetrainRequest(BaseModel):
    data_path: Optional[str] = None
