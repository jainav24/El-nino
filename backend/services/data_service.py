import random
import uuid
from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.database.models import (
    User, Farmer, WeatherRecord, EnsoRecord, 
    InsurancePolicy, InsuranceClaim, SurvivalDataset
)

def get_db_stats(db: Session):
    return {
        "total_users": db.query(User).count(),
        "total_farmers": db.query(Farmer).count(),
        "total_policies": db.query(InsurancePolicy).count(),
        "total_claims": db.query(InsuranceClaim).count(),
        "total_weather_records": db.query(WeatherRecord).count(),
        "total_enso_records": db.query(EnsoRecord).count(),
        "total_survival_records": db.query(SurvivalDataset).count(),
    }

def get_dataset_quality(db: Session):
    total = db.query(SurvivalDataset).count()
    if total == 0:
        return {
            "missing_values": {"enso_phase": 0, "rainfall": 0},
            "censorship_rate": 0.0,
            "total_records": 0,
            "el_nino_events": 0,
            "la_nina_events": 0,
            "neutral_events": 0
        }

    censored = db.query(SurvivalDataset).filter(SurvivalDataset.event == 0).count()
    el_nino = db.query(SurvivalDataset).filter(SurvivalDataset.enso_phase == "El Niño").count()
    la_nina = db.query(SurvivalDataset).filter(SurvivalDataset.enso_phase == "La Niña").count()
    neutral = db.query(SurvivalDataset).filter(SurvivalDataset.enso_phase == "Neutral").count()
    
    return {
        "missing_values": {
            "enso_phase": db.query(SurvivalDataset).filter(SurvivalDataset.enso_phase == None).count(),
            "rainfall": db.query(SurvivalDataset).filter(SurvivalDataset.rainfall == None).count(),
        },
        "censorship_rate": round(censored / total, 2),
        "total_records": total,
        "el_nino_events": el_nino,
        "la_nina_events": la_nina,
        "neutral_events": neutral
    }

def seed_demo_data(db: Session):
    db.query(SurvivalDataset).delete()
    db.query(InsuranceClaim).delete()
    db.query(InsurancePolicy).delete()
    db.query(Farmer).delete()
    db.query(WeatherRecord).delete()
    db.query(EnsoRecord).delete()
    db.commit()

    farmers_to_add = []
    policies_to_add = []
    claims_to_add = []
    
    # 15 Specific Demo Policies requested by the user
    demo_data = [
        {"pid": "POL-10001", "fid": "F-1001", "crop": "Wheat",  "region": "North",   "area": 8.5, "sum_insured": 200000.0, "rate": 2.0, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10002", "fid": "F-1002", "crop": "Rice",   "region": "East",    "area": 5.0, "sum_insured": 300000.0, "rate": 2.5, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10003", "fid": "F-1003", "crop": "Cotton", "region": "West",    "area": 6.2, "sum_insured": 150000.0, "rate": 3.0, "start": date(2026, 5, 1), "end": date(2026, 11, 1)},
        {"pid": "POL-10004", "fid": "F-1004", "crop": "Maize",  "region": "Central", "area": 4.0, "sum_insured": 250000.0, "rate": 2.0, "start": date(2026, 7, 1), "end": date(2027, 1, 1)},
        {"pid": "POL-10005", "fid": "F-1005", "crop": "Wheat",  "region": "North",   "area": 12.0,"sum_insured": 500000.0, "rate": 2.5, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10006", "fid": "F-1006", "crop": "Rice",   "region": "South",   "area": 3.5, "sum_insured": 200000.0, "rate": 1.5, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10007", "fid": "F-1007", "crop": "Cotton", "region": "West",    "area": 9.0, "sum_insured": 400000.0, "rate": 3.0, "start": date(2026, 5, 1), "end": date(2026, 11, 1)},
        {"pid": "POL-10008", "fid": "F-1008", "crop": "Maize",  "region": "East",    "area": 2.5, "sum_insured": 100000.0, "rate": 2.0, "start": date(2026, 7, 1), "end": date(2027, 1, 1)},
        {"pid": "POL-10009", "fid": "F-1009", "crop": "Wheat",  "region": "Central", "area": 7.0, "sum_insured": 300000.0, "rate": 2.5, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10010", "fid": "F-1010", "crop": "Rice",   "region": "North",   "area": 4.5, "sum_insured": 250000.0, "rate": 2.0, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10011", "fid": "F-1011", "crop": "Wheat",  "region": "South",   "area": 6.0, "sum_insured": 200000.0, "rate": 2.0, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10012", "fid": "F-1012", "crop": "Maize",  "region": "West",    "area": 8.0, "sum_insured": 400000.0, "rate": 2.5, "start": date(2026, 7, 1), "end": date(2027, 1, 1)},
        {"pid": "POL-10013", "fid": "F-1013", "crop": "Cotton", "region": "East",    "area": 5.5, "sum_insured": 300000.0, "rate": 3.0, "start": date(2026, 5, 1), "end": date(2026, 11, 1)},
        {"pid": "POL-10014", "fid": "F-1014", "crop": "Rice",   "region": "Central", "area": 10.0,"sum_insured": 500000.0, "rate": 2.5, "start": date(2026, 6, 1), "end": date(2026, 12, 1)},
        {"pid": "POL-10015", "fid": "F-1015", "crop": "Wheat",  "region": "North",   "area": 2.0, "sum_insured": 100000.0, "rate": 1.5, "start": date(2026, 6, 1), "end": date(2026, 12, 1)}
    ]

    for data in demo_data:
        farmer = Farmer(
            farmer_id=data["fid"],
            name=f"Demo Farmer {data['fid'].split('-')[1]}",
            region=data["region"],
            state="Demo State",
            district="Demo District",
            farm_area=data["area"],
            crop_type=data["crop"],
            soil_type="Loam",
            irrigation_type="Rainfed",
            sowing_date=data["start"],
            harvest_date=data["end"]
        )
        farmers_to_add.append(farmer)

        premium_amount = (data["sum_insured"] * data["rate"]) / 100.0
        policy = InsurancePolicy(
            policy_id=data["pid"],
            farmer_id=data["fid"],
            crop_type=data["crop"],
            region=data["region"],
            policy_start_date=data["start"],
            policy_end_date=data["end"],
            sum_insured=data["sum_insured"],
            premium_amount=premium_amount,
            premium_rate=data["rate"],
            coverage_type="Crop Insurance"
        )
        policies_to_add.append(policy)

    claims_list = [
        {"pid": "POL-10002", "cid": "CLM-10001", "amt": 50000.0},
        {"pid": "POL-10005", "cid": "CLM-10002", "amt": 150000.0},
        {"pid": "POL-10008", "cid": "CLM-10003", "amt": 25000.0}
    ]
    
    for cdata in claims_list:
        pol = next((p for p in policies_to_add if p.policy_id == cdata["pid"]), None)
        if pol:
            claim_date = pol.policy_start_date + timedelta(days=45)
            claim = InsuranceClaim(
                claim_id=cdata["cid"],
                policy_id=cdata["pid"],
                claim_date=claim_date,
                claim_status="Approved",
                claim_amount=cdata["amt"],
                claim_reason="El Niño Drought",
                event_occurred=1
            )
            claims_to_add.append(claim)

    regions = ["North", "South", "East", "West", "Central"]
    weather_to_add = []
    base_date = date.today().replace(day=1)
    for i in range(12):
        month_date = base_date - timedelta(days=30 * i)
        month_date = month_date.replace(day=1)
        for r in regions:
            weather_to_add.append(WeatherRecord(
                region=r,
                date=month_date,
                rainfall=random.uniform(50, 400),
                temperature=random.uniform(20, 38),
                humidity=random.uniform(30, 80),
                rainfall_anomaly_pct=random.uniform(-50, 50),
                temp_anomaly_c=random.uniform(-3, 3),
                drought_index=random.uniform(0.1, 1.0)
            ))
            
    enso_to_add = []
    for i in range(24):
        month_date = base_date - timedelta(days=30 * i)
        month_date = month_date.replace(day=1)
        rand_val = random.random()
        if rand_val < 0.3:
            phase = "El Niño"
            oni = random.uniform(0.5, 2.5)
            intensity = "Strong" if oni > 1.5 else "Moderate"
        elif rand_val > 0.7:
            phase = "La Niña"
            oni = random.uniform(-2.5, -0.5)
            intensity = "Strong" if oni < -1.5 else "Moderate"
        else:
            phase = "Neutral"
            oni = random.uniform(-0.5, 0.5)
            intensity = "Weak"
            
        enso_to_add.append(EnsoRecord(
            date=month_date,
            oni_value=oni,
            enso_phase=phase,
            enso_intensity=intensity,
            enso_duration=random.randint(3, 12)
        ))

    db.add_all(farmers_to_add)
    db.commit()
    
    db.add_all(policies_to_add)
    db.commit()
    
    db.add_all(claims_to_add)
    db.commit()
    
    db.add_all(weather_to_add)
    db.commit()
    
    db.add_all(enso_to_add)
    db.commit()

    return {"success": True, "message": "Successfully seeded 15 demo policies.", "records_inserted": 15}
