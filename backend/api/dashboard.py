from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database.connection import get_db
from backend.database.models import Farmer, InsurancePolicy, InsuranceClaim, WeatherRecord, EnsoRecord, SurvivalDataset

router = APIRouter()

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_farmers = db.query(func.count(Farmer.id)).scalar()
    total_policies = db.query(func.count(InsurancePolicy.id)).scalar()
    total_claims = db.query(func.count(InsuranceClaim.id)).scalar()
    total_weather = db.query(func.count(WeatherRecord.id)).scalar()
    total_enso = db.query(func.count(EnsoRecord.id)).scalar()
    total_survival = db.query(func.count(SurvivalDataset.id)).scalar()
    
    total_events = db.query(func.count(SurvivalDataset.id)).filter(SurvivalDataset.event == 1).scalar()
    total_censored = db.query(func.count(SurvivalDataset.id)).filter(SurvivalDataset.event == 0).scalar()
    
    claim_rate = (total_claims / total_policies * 100) if total_policies > 0 else 0
    
    return {
        "total_farmers": total_farmers,
        "total_policies": total_policies,
        "total_claims": total_claims,
        "total_weather_records": total_weather,
        "total_enso_records": total_enso,
        "total_survival_records": total_survival,
        "total_events": total_events,
        "total_censored": total_censored,
        "claim_rate_percentage": round(claim_rate, 2)
    }

@router.get("/dashboard/analytics")
def get_advanced_analytics(db: Session = Depends(get_db)):
    """Advanced analytics for the reporting layer."""
    # ENSO Frequencies
    enso_records = db.query(EnsoRecord).all()
    enso_dist = {"El Niño": 0, "La Niña": 0, "Neutral": 0}
    oni_trend = []
    for er in enso_records:
        if er.enso_phase in enso_dist:
            enso_dist[er.enso_phase] += 1
        oni_trend.append({"date": er.date.strftime("%Y-%m"), "oni": er.oni_value, "phase": er.enso_phase})
    
    # Sort oni trend
    oni_trend.sort(key=lambda x: x["date"])

    # Insurance / Regional Risk Map data
    policies = db.query(InsurancePolicy.region, InsurancePolicy.crop_type).all()
    claims = db.query(InsuranceClaim.claim_amount, InsurancePolicy.region, InsurancePolicy.crop_type)\
        .join(InsurancePolicy, InsuranceClaim.policy_id == InsurancePolicy.policy_id).all()
        
    claims_by_region = {}
    claims_by_crop = {}
    claim_amount_dist = []
    
    for c in claims:
        r = c.region
        crop = c.crop_type
        amt = c.claim_amount or 0
        claims_by_region[r] = claims_by_region.get(r, 0) + 1
        claims_by_crop[crop] = claims_by_crop.get(crop, 0) + 1
        claim_amount_dist.append(amt)
        
    regional_risk = []
    for r, count in claims_by_region.items():
        regional_risk.append({"region": r, "claims": count})

    # Claim reasons (Mocked or aggregated if available, in this DB we have claim_reason)
    reasons = db.query(InsuranceClaim.claim_reason, func.count(InsuranceClaim.id))\
        .group_by(InsuranceClaim.claim_reason).all()
    reason_dist = [{"reason": r[0] or "Unknown", "count": r[1]} for r in reasons]
    
    # Claims over time (grouped by month-year)
    claims_history = db.query(InsuranceClaim.claim_date, func.count(InsuranceClaim.id))\
        .group_by(InsuranceClaim.claim_date).all()
        
    # Group by month
    from collections import defaultdict
    time_grouped = defaultdict(int)
    for c_date, count in claims_history:
        month = c_date.strftime("%Y-%m")
        time_grouped[month] += count
    
    claims_over_time = [{"month": k, "claims": v} for k, v in sorted(time_grouped.items())]
    
    return {
        "enso": {
            "frequency": enso_dist,
            "oni_trend": oni_trend[-24:] # Last 24 months
        },
        "insurance": {
            "claims_by_region": regional_risk,
            "claims_by_crop": [{"crop": c, "claims": v} for c, v in claims_by_crop.items()],
            "reason_dist": reason_dist,
            "claim_amount_avg": sum(claim_amount_dist) / len(claim_amount_dist) if claim_amount_dist else 0,
            "claims_over_time": claims_over_time
        }
    }
