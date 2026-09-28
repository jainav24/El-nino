from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import pandas as pd
import uuid
import os
import joblib
from pydantic import BaseModel

from backend.database.connection import get_db
from backend.database.models import SurvivalDataset, ModelVersion
from backend.ml.pipeline import build_survival_dataset, train_cox_model
from backend.ml.kaplan_meier import get_kaplan_meier_curves
from backend.ml.prediction import predict_risk, get_active_model_info

router = APIRouter()

class PredictionRequest(BaseModel):
    farmer_id: str = ""
    policy_id: str = ""
    region: str = ""
    crop_type: str = ""
    farm_area_acres: float = 1.0
    soil_type: str = ""
    irrigation: str = ""
    policy_start: str = ""
    policy_end: str = ""
    duration_months: int = 6
    sum_insured: float = 0.0
    premium_amount: float = 0.0
    premium_rate: float = 0.0
    
    rainfall_mm: float = 0.0
    rainfall_anomaly_pct: float = 0.0
    temperature_c: float = 0.0
    temp_anomaly_c: float = 0.0
    humidity_pct: float = 0.0
    drought_index: float = 0.0
    
    enso_phase: str = "Neutral"
    oni: float = 0.0
    enso_intensity: str = "Neutral"

@router.post("/train")
def train_model(db: Session = Depends(get_db)):
    """Extracts survival dataset and triggers full training pipeline."""
    # 1. Build Survival Dataset
    num_records = build_survival_dataset(db)
    
    # 2. Train Cox Model
    report = train_cox_model(db)
    
    # 3. Save ModelVersion to DB
    c_index = report.get('c_index', 0.0)
    version_str = f"v-{uuid.uuid4().hex[:8]}"
    
    mv = ModelVersion(
        version=version_str,
        dataset_size=num_records,
        features_used=",".join(report.get('features', [])),
        algorithm="Cox Proportional Hazards",
        c_index=c_index,
        is_active=True # auto-activate newest for simplicity
    )
    # deactivate others
    db.query(ModelVersion).update({ModelVersion.is_active: False})
    db.add(mv)
    db.commit()
    
    return {"status": "success", "report": report, "version": version_str}

@router.get("/versions")
def get_model_versions(db: Session = Depends(get_db)):
    return db.query(ModelVersion).order_by(ModelVersion.timestamp.desc()).all()

@router.get("/kaplan-meier")
def kaplan_meier_analysis(group_by: str = None, db: Session = Depends(get_db)):
    try:
        results = get_kaplan_meier_curves(db, group_by=group_by)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from backend.database.models import Farmer, InsurancePolicy, WeatherRecord, EnsoRecord

@router.get("/policy-context/{policy_id}")
def get_policy_context(policy_id: str, db: Session = Depends(get_db)):
    policy = db.query(InsurancePolicy).filter(InsurancePolicy.policy_id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    farmer = db.query(Farmer).filter(Farmer.farmer_id == policy.farmer_id).first()
    
    # Get latest weather for region
    weather = db.query(WeatherRecord).filter(WeatherRecord.region == policy.region).order_by(WeatherRecord.date.desc()).first()
    
    # Get latest ENSO
    enso = db.query(EnsoRecord).order_by(EnsoRecord.date.desc()).first()
    
    duration_months = 0
    if policy.policy_start_date and policy.policy_end_date:
        delta = policy.policy_end_date - policy.policy_start_date
        duration_months = max(1, round(delta.days / 30.0))

    return {
        "policy_id": policy.policy_id,
        "farmer_id": farmer.farmer_id if farmer else "Unknown",
        "crop_type": policy.crop_type,
        "region": policy.region,
        "farm_area_acres": farmer.farm_area if farmer else 1.0,
        "soil_type": farmer.soil_type if farmer else "Loam",
        "irrigation": farmer.irrigation_type if farmer else "Rainfed",
        "policy_start": policy.policy_start_date.isoformat() if policy.policy_start_date else "",
        "policy_end": policy.policy_end_date.isoformat() if policy.policy_end_date else "",
        "duration_months": duration_months,
        "sum_insured": policy.sum_insured,
        "premium_amount": policy.premium_amount,
        "premium_rate": policy.premium_rate,
        
        "temperature_c": weather.temperature_c if weather and weather.temperature_c is not None else 25.0,
        "temp_anomaly_c": weather.temp_anomaly_c if weather and weather.temp_anomaly_c is not None else 0.0,
        "rainfall_mm": weather.rainfall_mm if weather and weather.rainfall_mm is not None else 100.0,
        "rainfall_anomaly_pct": weather.rainfall_anomaly_pct if weather and weather.rainfall_anomaly_pct is not None else 0.0,
        "humidity_pct": weather.humidity_pct if weather and weather.humidity_pct is not None else 60.0,
        "drought_index": weather.drought_index if weather and weather.drought_index is not None else 0.0,
        
        "enso_phase": enso.enso_phase if enso else "Neutral",
        "oni": enso.oni_value if enso else 0.0,
        "enso_intensity": enso.enso_intensity if enso and hasattr(enso, 'enso_intensity') else "Neutral"
    }

@router.post("/predict")
def predict_individual_risk(req: PredictionRequest, db: Session = Depends(get_db)):
    try:
        prediction = predict_risk(req.model_dump())
        
        active_model = db.query(ModelVersion).filter(ModelVersion.is_active == True).first()
        version_id = active_model.version if active_model else "Unknown"
        
        prediction["model_version"] = version_id
        
        # RiskAssessment frontend expects survival_probabilities object, 
        # and also expects hazard_ratio (prediction.py returns relative_hazard)
        if "relative_hazard" in prediction:
            prediction["hazard_ratio"] = prediction.pop("relative_hazard")
            
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
