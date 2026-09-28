from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from backend.database.connection import get_db
from backend.database.models import PredictionHistory
from backend.schemas.request import PredictionRequest, WhatIfRequest, RetrainRequest
from backend.schemas.response import (
    PredictionResponse, WhatIfResponse, HealthResponse,
    ModelInfoResponse, StatisticsResponse, HistoryResponse, HistoryItem
)
from backend.services.prediction_service import run_prediction, run_what_if
from backend.services.retrain_service import run_retraining
from backend.config import APP_VERSION, MODEL_VERSION
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# ──────────────────────────────────────────────
# 1. Prediction Endpoints
# ──────────────────────────────────────────────

@router.post("/predict", response_model=PredictionResponse)
def predict_risk(request_data: PredictionRequest, request: Request, db: Session = Depends(get_db)):
    """Evaluate agricultural policy risk using the Cox PH Survival Model."""
    logger.info("Received prediction request")
    engine = request.app.state.risk_engine
    
    response = run_prediction(engine, db, request_data)
    if not response.success:
        logger.error(f"Prediction failed with errors: {response.errors}")
        raise HTTPException(status_code=400, detail=response.errors)
        
    return response


@router.post("/what-if", response_model=WhatIfResponse)
def what_if_analysis(request_data: WhatIfRequest, request: Request):
    """Compare two scenarios to see how risk changes."""
    logger.info("Received what-if analysis request")
    engine = request.app.state.risk_engine
    
    response = run_what_if(engine, request_data)
    if not response.success:
        logger.error(f"What-if analysis failed with errors: {response.errors}")
        raise HTTPException(status_code=400, detail=response.errors)
        
    return response


# ──────────────────────────────────────────────
# 2. System Endpoints
# ──────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
def health_check(request: Request):
    """Check API health and model status."""
    engine_loaded = hasattr(request.app.state, "risk_engine") and request.app.state.risk_engine is not None
    return HealthResponse(
        status="healthy",
        model_loaded=engine_loaded,
        version=APP_VERSION
    )


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info(request: Request):
    """Retrieve metadata about the currently loaded survival model."""
    engine = request.app.state.risk_engine
    model = engine.cox_model
    
    # Read evaluation report for concordance indices if available
    try:
        from backend.config import MODEL_OUTPUT_DIR
        import os
        report_path = os.path.join(MODEL_OUTPUT_DIR, "cph_evaluation_report.txt")
        with open(report_path, "r") as f:
            content = f.read()
            # Extract C-Indices using simple string matching
            b_idx = content.find("Baseline Model C-Index")
            p_idx = content.find("Proposed Model C-Index")
            baseline_c = float(content[b_idx:b_idx+50].split(":")[1].strip())
            proposed_c = float(content[p_idx:p_idx+50].split(":")[1].strip())
    except Exception:
        baseline_c = 0.0
        proposed_c = getattr(model, "concordance_index_", 0.0)

    return ModelInfoResponse(
        version=MODEL_VERSION,
        description="Cox Proportional Hazards model with El Niño interaction features",
        baseline_concordance=baseline_c,
        proposed_concordance=proposed_c,
        feature_count=len(model.params_)
    )


@router.post("/retrain")
def retrain_model(request_data: RetrainRequest, request: Request):
    """Trigger the backend ML pipeline to retrain and reload the model in memory."""
    logger.info("Received retrain request")
    success = run_retraining(request.app.state, request_data.data_path)
    if not success:
        raise HTTPException(status_code=500, detail="Retraining pipeline failed. Check server logs.")
    return {"message": "Model retrained and loaded successfully"}


# ──────────────────────────────────────────────
# 3. Database / Statistics Endpoints
# ──────────────────────────────────────────────

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """Get aggregated statistics from historical predictions."""
    total = db.query(func.count(PredictionHistory.id)).scalar()
    
    if total == 0:
        return StatisticsResponse(
            total_predictions=0,
            average_risk_score=0.0,
            risk_category_distribution={}
        )
        
    avg_score = db.query(func.avg(PredictionHistory.risk_score)).scalar()
    
    cats = db.query(PredictionHistory.risk_category, func.count(PredictionHistory.id))\
             .group_by(PredictionHistory.risk_category).all()
             
    dist = {c[0]: c[1] for c in cats if c[0] is not None}
    
    return StatisticsResponse(
        total_predictions=total,
        average_risk_score=float(avg_score) if avg_score else 0.0,
        risk_category_distribution=dist
    )


@router.get("/history", response_model=HistoryResponse)
def get_history(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve paginated prediction history."""
    total = db.query(func.count(PredictionHistory.id)).scalar()
    
    records = db.query(PredictionHistory)\
                .order_by(PredictionHistory.timestamp.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
                
    items = []
    for r in records:
        items.append(HistoryItem(
            id=r.id,
            timestamp=r.timestamp,
            state=r.state or "Unknown",
            crop_type=r.crop_type or "Unknown",
            risk_score=r.risk_score or 0.0,
            risk_category=r.risk_category or "Unknown",
            explanation=r.explanation or ""
        ))
        
    return HistoryResponse(items=items, total=total)
