from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database.connection import get_db
from backend.database.models import Farmer, InsurancePolicy, InsuranceClaim, WeatherRecord, EnsoRecord
from pydantic import BaseModel
from datetime import date

from backend.ml.prediction import get_active_model_info

router = APIRouter()

@router.get("/health")
def check_health(db: Session = Depends(get_db)):
    model_active = get_active_model_info()
    return {
        "status": "healthy",
        "model_loaded": model_active is not None
    }

# --- Schemas ---
class FarmerBase(BaseModel):
    farmer_id: str
    name: str
    region: str
    state: str
    farm_area: float
    crop_type: str

class FarmerCreate(FarmerBase):
    pass

class FarmerOut(FarmerBase):
    id: int
    class Config:
        from_attributes = True

class PolicyBase(BaseModel):
    policy_id: str
    farmer_id: str
    crop_type: str
    region: str
    policy_start_date: date
    policy_end_date: date
    sum_insured: float
    premium_amount: float
    premium_rate: float | None = None
    coverage_type: str | None = None

class PolicyCreate(PolicyBase):
    pass

class PolicyOut(PolicyBase):
    id: int
    class Config:
        from_attributes = True

class ClaimBase(BaseModel):
    claim_id: str
    policy_id: str
    claim_date: date
    claim_status: str
    claim_amount: float
    claim_reason: str

class ClaimCreate(ClaimBase):
    pass

class ClaimOut(ClaimBase):
    id: int
    class Config:
        from_attributes = True

class WeatherOut(BaseModel):
    id: int
    region: str
    date: date
    rainfall: float
    temperature: float
    humidity: float
    wind_speed: float
    soil_moisture: float
    drought_index: float | None = None
    
    class Config:
        from_attributes = True

class EnsoOut(BaseModel):
    id: int
    date: date
    oni_value: float
    enso_phase: str
    enso_intensity: str | None = None
    enso_duration: int | None = None
    
    class Config:
        from_attributes = True

# --- Farmer Endpoints ---
@router.post("/farmers", response_model=FarmerOut)
def create_farmer(farmer: FarmerCreate, db: Session = Depends(get_db)):
    db_farmer = Farmer(**farmer.model_dump())
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return db_farmer

@router.get("/farmers", response_model=List[FarmerOut])
def list_farmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Farmer).offset(skip).limit(limit).all()

# --- Policy Endpoints ---
@router.post("/policies", response_model=PolicyOut)
def create_policy(policy: PolicyCreate, db: Session = Depends(get_db)):
    db_policy = InsurancePolicy(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.get("/policies", response_model=List[PolicyOut])
def list_policies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(InsurancePolicy).offset(skip).limit(limit).all()

# --- Claim Endpoints ---
@router.post("/claims", response_model=ClaimOut)
def create_claim(claim: ClaimCreate, db: Session = Depends(get_db)):
    db_claim = InsuranceClaim(**claim.model_dump())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

@router.get("/claims", response_model=List[ClaimOut])
def list_claims(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(InsuranceClaim).offset(skip).limit(limit).all()

# --- Weather & ENSO Endpoints ---
@router.get("/weather", response_model=List[WeatherOut])
def list_weather(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(WeatherRecord).offset(skip).limit(limit).all()

@router.get("/enso", response_model=List[EnsoOut])
def list_enso(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(EnsoRecord).offset(skip).limit(limit).all()

# --- Insurance Quote Endpoint ---
class QuoteRequest(BaseModel):
    sum_insured: float
    policy_duration_months: int
    crop_type: str
    region: str

class QuoteResponse(BaseModel):
    sum_insured: float
    premium_rate: float
    premium_amount: float
    policy_duration_months: int
    currency: str = "INR"

@router.post("/insurance/quote", response_model=QuoteResponse)
def calculate_quote(request: QuoteRequest):
    if request.sum_insured <= 0:
        raise HTTPException(status_code=400, detail="Sum insured must be greater than 0")
        
    from backend.config import DEFAULT_PREMIUM_RATE
    
    premium_amount = request.sum_insured * DEFAULT_PREMIUM_RATE / 100.0
    
    return QuoteResponse(
        sum_insured=request.sum_insured,
        premium_rate=DEFAULT_PREMIUM_RATE,
        premium_amount=premium_amount,
        policy_duration_months=request.policy_duration_months
    )
