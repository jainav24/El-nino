import os
import sys
from backend.config import RAW_DATA_PATH, PIPELINE_OUTPUT_DIR, MODEL_OUTPUT_DIR
from backend.utils.logger import get_logger

# Import the ML pipelines
from backend.ml.feature_engineering import FeatureEngineeringPipeline
from backend.ml.survival_model import SurvivalAnalysisPipeline
from backend.ml.risk_engine import RiskEngine

logger = get_logger(__name__)

def run_retraining(app_state, custom_data_path: str = None) -> bool:
    """
    Executes the feature engineering and survival model pipelines.
    Then re-instantiates the RiskEngine and attaches it to the FastAPI app state.
    """
    try:
        data_path = custom_data_path if custom_data_path else RAW_DATA_PATH
        
        logger.info(f"Starting retraining process with data: {data_path}")
        
        # 1. Feature Engineering
        logger.info("Step 1/2: Feature Engineering...")
        fe_pipeline = FeatureEngineeringPipeline(
            raw_data_path=data_path,
            output_dir=PIPELINE_OUTPUT_DIR
        )
        fe_pipeline.run()
        
        # 2. Survival Model
        logger.info("Step 2/2: Survival Model Training...")
        ml_data_path = os.path.join(PIPELINE_OUTPUT_DIR, "survival_analysis_dataset.csv")
        ml_pipeline = SurvivalAnalysisPipeline(
            data_path=ml_data_path,
            output_dir=MODEL_OUTPUT_DIR
        )
        ml_pipeline.run()
        
        # 3. Reload Engine
        logger.info("Reloading RiskEngine in memory...")
        app_state.risk_engine = RiskEngine()
        
        logger.info("Retraining complete.")
        return True
    except Exception as e:
        logger.error(f"Retraining failed: {str(e)}", exc_info=True)
        return False
