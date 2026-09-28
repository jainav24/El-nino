import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    state = Column(String, index=True)
    crop_type = Column(String, index=True)
    risk_score = Column(Float)
    risk_category = Column(String, index=True)
    claim_probability_180d = Column(Float)
    estimated_time_to_claim = Column(String)
    explanation = Column(Text)
    raw_request = Column(Text)
    raw_response = Column(Text)

    def set_request(self, data_dict):
        self.raw_request = json.dumps(data_dict)
        
    def set_response(self, data_dict):
        self.raw_response = json.dumps(data_dict)
        
    def get_request(self):
        return json.loads(self.raw_request) if self.raw_request else {}
        
    def get_response(self):
        return json.loads(self.raw_response) if self.raw_response else {}

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user") # e.g., admin, analyst
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    region = Column(String, index=True)
    state = Column(String, index=True)
    district = Column(String)
    farm_area = Column(Float) # in hectares
    crop_type = Column(String, index=True)
    soil_type = Column(String)
    irrigation_type = Column(String)
    sowing_date = Column(Date)
    harvest_date = Column(Date)
    
    policies = relationship("InsurancePolicy", back_populates="farmer")

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    rainfall = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall_anomaly_pct = Column(Float)
    temp_anomaly_c = Column(Float)
    drought_index = Column(Float, nullable=True)

class EnsoRecord(Base):
    __tablename__ = "enso_records"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False) # Representing the month
    oni_value = Column(Float, nullable=False)
    enso_phase = Column(String, nullable=False) # El Niño, Neutral, La Niña
    enso_intensity = Column(String) # Weak, Moderate, Strong, Very Strong
    enso_duration = Column(Integer) # Duration in months

class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String, unique=True, index=True, nullable=False)
    farmer_id = Column(String, ForeignKey("farmers.farmer_id"), nullable=False)
    crop_type = Column(String, index=True)
    region = Column(String, index=True)
    policy_start_date = Column(Date, nullable=False)
    policy_end_date = Column(Date, nullable=False)
    sum_insured = Column(Float, nullable=False)
    premium_amount = Column(Float, nullable=False)
    premium_rate = Column(Float)
    coverage_type = Column(String)
    policy_status = Column(String, default="Active")
    
    farmer = relationship("Farmer", back_populates="policies")
    claims = relationship("InsuranceClaim", back_populates="policy")

class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, unique=True, index=True, nullable=False)
    policy_id = Column(String, ForeignKey("insurance_policies.policy_id"), nullable=False)
    claim_date = Column(Date, nullable=False)
    claim_status = Column(String, nullable=False) # Approved, Rejected, Pending
    claim_amount = Column(Float)
    claim_reason = Column(String)
    event_occurred = Column(Integer, default=1) # 1 = claim occurred
    
    policy = relationship("InsurancePolicy", back_populates="claims")

class SurvivalDataset(Base):
    """
    Derived dataset containing pre-computed variables for the Survival Analysis model.
    """
    __tablename__ = "survival_dataset"
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String, ForeignKey("insurance_policies.policy_id"), unique=True, nullable=False)
    farmer_id = Column(String, nullable=False)
    
    # Target Variables
    event = Column(Integer, nullable=False) # 1 = claim occurred, 0 = right-censored
    duration_days = Column(Integer, nullable=False) # Time-to-event or censoring time (days)
    
    # Weather
    rainfall_mm = Column(Float)
    temperature_c = Column(Float)
    humidity_pct = Column(Float)
    
    # Weather Derived
    rainfall_anomaly_pct = Column(Float)
    temp_anomaly_c = Column(Float)
    drought_index = Column(Float)
    
    # ENSO
    oni = Column(Float)
    enso_phase = Column(String)
    enso_intensity = Column(String)
    
    # Agricultural
    crop_type = Column(String)
    region = Column(String)
    farm_area_acres = Column(Float)
    soil_type = Column(String)
    irrigation = Column(String)
    
    policy = relationship("InsurancePolicy")

class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True, nullable=False)
    dataset_size = Column(Integer)
    features_used = Column(String)
    algorithm = Column(String)
    c_index = Column(Float)
    brier_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=False)
