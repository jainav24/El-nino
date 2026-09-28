# Research Gap & Proposed System Architecture

This document explicitly defines the academic and practical gap in current agricultural insurance underwriting models, and how the proposed system addresses it.

## 1. Existing Systems vs. Proposed System

### 1.1 The Existing Approach

Traditional agricultural risk modeling systems, particularly in developing regions, suffer from several critical limitations:
- **Binary Predictions**: Most models frame the problem as a simple binary classification ("Will a claim occur: Yes or No?"). This ignores *when* a claim might occur, which is crucial for financial liquidity planning in insurance.
- **Siloed Variables**: Existing models often use generic weather data or agricultural variables separately. They do not calculate complex interaction terms (e.g., how the *same* rainfall deficit affects a *drought-resistant* crop vs a *standard* crop).
- **Ignoring Time-to-Claim**: By using Logistic Regression, Random Forest, or XGBoost for binary classification, current models cannot handle *right-censored* data (policies that ended without a claim but were at risk).
- **Limited Climate Interpretation**: El Niño and La Niña are often completely ignored, or treated as simple categorical variables rather than complex, long-lasting climatic drivers that interact uniquely with regional geography.

### 1.2 The Proposed Approach

Our proposed model, the **AI-Driven Risk Assessment Model for Agricultural Insurance Claims under El Niño Weather Anomalies**, bridges these gaps using a multi-disciplinary approach:

- **Survival Analysis Integration**: By utilizing Kaplan-Meier estimators and the Cox Proportional Hazards (CPH) model, we shift the paradigm from *classification* (Yes/No) to *time-to-event* modeling (Hazard Rate over time). This allows the system to accurately handle right-censored policy data.
- **Deep Feature Engineering**: We integrate agricultural variables, insurance policy parameters, local weather data, and explicit El Niño intensity metrics.
- **Interaction Modeling**: We calculate multiplicative interaction features (e.g., `El Niño × Rainfall Deviation`, `Crop Type × Drought`) to capture the compound nature of climate risks.
- **Explainable Risk Scoring**: The model produces a transparent `Preliminary Weather Risk Score` alongside hazard ratios, allowing underwriters to explicitly see *why* a policy is deemed high-risk.
- **Empirical Climate Validation**: Our evaluation explicitly isolates the El Niño features, comparing a baseline model against an El-Niño-aware model to mathematically prove the value of long-term climatic predictors in actuarial science.

---

## 2. Research Hypothesis

**Hypothesis**: The integration of explicit El Niño intensity markers and their interaction with localized weather anomalies significantly improves the concordance (C-index) of Survival Analysis models in predicting agricultural insurance claims, compared to models using only baseline weather telemetry.

## 3. Workflow Progression

Our methodology follows this structured progression:
1. **Dataset Design & Synthetic Generation**: Bridging the gap of proprietary insurance data scarcity.
2. **El Niño & Weather Feature Engineering**: Mapping physical climate phenomena into machine-learning predictors.
3. **Survival Dataset Construction**: Establishing `duration` and `event` parameters.
4. **Cox Proportional Hazards Model (CPH)**: Training the core statistical ML module.
5. **Model Evaluation & Hazard Ratio Extraction**: Validating the research hypothesis.
6. **Explainable Risk Engine Backend (FastAPI)**: Deploying the model for inference.
7. **Interactive Dashboard (React)**: Providing an underwriter interface for dynamic risk assessment.
