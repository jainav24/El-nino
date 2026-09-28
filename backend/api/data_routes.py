from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.database.connection import get_db
from backend.schemas.data_schemas import DBStatsResponse, DatasetQualityResponse, CSVImportResponse
from backend.services.data_service import get_db_stats, get_dataset_quality, seed_demo_data
from backend.services.data_upload import validate_csv_content, process_and_store_csv

router = APIRouter()

@router.get("/statistics", response_model=DBStatsResponse)
def database_statistics(db: Session = Depends(get_db)):
    """Retrieve database counts and statistics."""
    try:
        return get_db_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset-quality", response_model=DatasetQualityResponse)
def dataset_quality(db: Session = Depends(get_db)):
    """Check dataset quality for Survival Analysis (censorship rate, missing values)."""
    try:
        return get_dataset_quality(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed", response_model=CSVImportResponse)
def seed_database(db: Session = Depends(get_db)):
    """Seed the database with realistic DEMO DATA for development."""
    try:
        result = seed_demo_data(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-csv")
async def validate_csv(file: UploadFile = File(...), dataset_type: str = Form(...), db: Session = Depends(get_db)):
    """Validates the CSV before storage."""
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        
    content = await file.read()
    result = validate_csv_content(content, dataset_type, db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result

@router.post("/store-csv")
async def store_csv(file: UploadFile = File(...), dataset_type: str = Form(...), db: Session = Depends(get_db)):
    """Stores the CSV in the database."""
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        
    content = await file.read()
    result = process_and_store_csv(content, dataset_type, db)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
        
    return result
