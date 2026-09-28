from sqlalchemy.orm import Session
from backend.database.models import PredictionHistory
from backend.schemas.request import PredictionRequest, WhatIfRequest
from backend.schemas.response import PredictionResponse, WhatIfResponse, ChangedInput
from backend.config import MODEL_VERSION
import json

def run_prediction(engine, db: Session, request: PredictionRequest) -> PredictionResponse:
    # Convert Pydantic model to dict
    req_dict = request.model_dump()
    
    # Run the engine
    result = engine.predict(req_dict)
    
    if not result.get("success"):
        return PredictionResponse(success=False, errors=result.get("errors"))
        
    # Append model version
    result["model_version"] = MODEL_VERSION
    
    # Save to database
    history_record = PredictionHistory(
        state=req_dict.get("state"),
        crop_type=req_dict.get("crop_type"),
        risk_score=result.get("overall_risk_score"),
        risk_category=result.get("risk_category"),
        claim_probability_180d=result.get("claim_probability", {}).get("180_days"),
        estimated_time_to_claim=result.get("estimated_time_to_claim"),
        explanation=result.get("explanation")
    )
    history_record.set_request(req_dict)
    history_record.set_response(result)
    
    db.add(history_record)
    db.commit()
    db.refresh(history_record)
    
    # Convert to Response schema
    return PredictionResponse(**result)


def run_what_if(engine, request: WhatIfRequest) -> WhatIfResponse:
    curr_dict = request.current_scenario.model_dump()
    alt_dict = request.alternative_scenario.model_dump()
    
    result = engine.what_if_analysis(curr_dict, alt_dict)
    
    if not result.get("success"):
        return WhatIfResponse(success=False, errors=result.get("errors"))
        
    # Map 'from' dict keys back properly for pydantic (since 'from' is reserved)
    if "changed_inputs" in result:
        mapped_changed = {}
        for k, v in result["changed_inputs"].items():
            mapped_changed[k] = {"from_": v["from"], "to": v["to"]}
        result["changed_inputs"] = mapped_changed
        
    return WhatIfResponse(**result)
