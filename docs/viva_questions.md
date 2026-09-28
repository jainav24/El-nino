# Viva Preparation: Questions & Answers

## 1. Why did you use Survival Analysis instead of Logistic Regression?
**Answer:** Traditional binary classifiers (like Logistic Regression) only predict *if* a claim will happen. Survival Analysis predicts *when* a claim will happen. By using the Cox Proportional Hazards model, we can model the time-to-event over the 365-day crop cycle, accounting for policies that survive the entire year without a claim (right-censored data). It also natively supports dynamic baseline hazards.

## 2. What is Data Leakage, and how did you prevent it?
**Answer:** Data Leakage occurs when a model is trained using features that wouldn't be available at prediction time, artificially inflating accuracy. For example, if we include `final_crop_yield` or `claim_count` as an input to predict the claim probability, the model is "cheating." We prevented this by rigorously auditing our synthetic dataset and removing any post-event outcomes from the feature engineering pipeline.

## 3. How did you incorporate El Niño into the model?
**Answer:** We used the Oceanic Niño Index (ONI) to derive features like `enso_index`, `el_nino_indicator` (binary), and `elnino_intensity`. Crucially, we didn't just feed raw ENSO numbers into the model. We engineered **interaction terms** (e.g., `el_nino_indicator * rainfall_deviation`) to mathematically capture how El Niño *amplifies* existing vulnerabilities, like drought or poor irrigation.

## 4. What is a Hazard Ratio?
**Answer:** A Hazard Ratio is the exponentiated coefficient of a feature in the Cox model (`exp(coef)`). A ratio > 1 means the feature increases the risk (accelerates the time to claim). A ratio < 1 means the feature decreases the risk (protective). We use this to provide Explainable AI (XAI) directly to the user interface.

## 5. What is the Concordance Index (C-Index)?
**Answer:** The C-Index is the standard evaluation metric for survival models. It measures the rank correlation between predicted risk and actual observed survival times. A C-Index of 0.5 is random guessing, while 1.0 is perfect. Our proposed model achieved ~0.73, outperforming the baseline model (~0.72) which didn't include El Niño features.

## 6. How does the "What-If" Analysis work?
**Answer:** The FastAPI backend exposes an endpoint that accepts two distinct scenarios: `current` and `alternative`. It processes both through the feature engineering pipeline, generates two separate predictions using the Cox model, and computes the delta in the overall risk score. This proves that our model reacts dynamically to mitigation strategies (like upgrading to Drip irrigation).

## 7. How did you ensure deterministic behavior during inference?
**Answer:** During inference (predicting a single row from the frontend), tools like `LabelEncoder` or `StandardScaler` cannot use `fit_transform()`, because the encoding would change depending on the single input value. We solved this by serializing (pickling) the `StandardScaler` used during training, and hardcoding a fixed categorical ordinal mapping for features like `crop_type` and `state`.
