# Machine Learning Methodology

The pipeline shifts away from Binary Classification to Time-To-Event modeling.

## 1. Preprocessing
- Identification of Missing Values (NaN)
- Strict exclusion of operative ID variables to prevent Data Leakage.
- One-Hot Encoding for categorical features (`Crop_Type`, `Region`).

## 2. Feature Selection
Features are strictly restricted to those available at the inception of the policy. ENSO parameters (`avg_oni_value`, `primary_enso_phase`) are aligned temporally.

## 3. Training Framework
Models are trained utilizing the `lifelines` library. Models are inherently versioned locally and explicitly tracked via the `ModelVersion` database table to track Concordance Index (C-Index) drift over time.
